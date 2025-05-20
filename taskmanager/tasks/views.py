from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .maxins import SprintTaskWithinRangeMixin
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    Http404,
    JsonResponse,
)
from tasks.services.task_services import (
    create_task_and_add_to_sprint,
    claim_task,
    TaskAlreadyClaimedException,
    remove_task_from_sprint,
    check_task,
)
from tasks.services.sprint_services import create_sprint, set_sprint_epic
from tasks.models import Task, Sprint, Epic
from rest_framework import status
from django.conf import settings
from collections import defaultdict
from tasks.forms import TaskForm, ContactForm, EpicFormSet, SprintForm, SprintFormSet, EpicForm
from tasks.services.services import send_contact_email
from tasks.services.epic_services import (
    get_epic_by_id,
    get_task_by_epic,
    save_task_for_epic,
)
from tasks.services.sprint_services import (
    get_task_by_id,
    get_sprint_by_task,
    save_sprint_for_task,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model


User = get_user_model()


# Create your views here.


# LoginRequiredMixin added before any Generic Views, which will protect from accessing class-based-view from unauthenticated user
# @method_decorator(login_required, name='dispatch')
class TaskListView(PermissionRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    permission_required = ("tasks.view_task", "tasks.custom_task")
    login_url = "accounts/login/"
    raise_exception = True


class TaskDetailView(DetailView):
    model = Task
    template_name = "tasks/task_details.html"
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, SprintTaskWithinRangeMixin, CreateView):
    model = Task
    template_name = "tasks/task_form.html"
    # fields = ['title', 'description', 'start_date', 'end_date']
    form_class = TaskForm

    def form_valid(self, form):
        # Set the creator to the currently logged-in user
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.id})


class TaskUpdateView(PermissionRequiredMixin, SprintTaskWithinRangeMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    permission_required = ("tasks.change_task",)

    def form_valid(self, form):
        # Set the creator to the currently logged-in user
        form.instance.creator = self.request.user
        return super().form_valid(form)

    # Call the parent class's has_permission() method
    def has_permission(self):
        # check, if the user has general permision to edit the task
        has_general_permission = super().has_permission()

        if not has_general_permission:
            # Deny access if the general permission is not granted
            return False

        # Retrieve the task instance
        task_id = self.kwargs.get("pk")
        task = get_object_or_404(Task, pk=task_id)

        # Then check user is either creator or owner of the task
        is_creator_or_owner = (
            task.creator == self.request.user or task.owner == self.request.user
        )

        return is_creator_or_owner

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.id})


class TaskDeleteView(PermissionRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:task-list")
    permission_required = "tasks.delete_task"


# function based view
def check_task(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        # extract the task_id parameter from post date
        task_id = request.POST.get("task_id")

        if check_task(task_id):
            return HttpResponseRedirect(reverse("success"))

        if task_id:
            return HttpResponseRedirect(reverse("success"))
        else:
            # If task_id is not provided, re-render the form with an error message
            return render(
                request, "add_task_to_sprint.html", {"error": "Task ID is required"}
            )
    else:
        # if request method is not post just render the form
        return render(request, "tasks/check_task.html")


# @login_required
@permission_required("tasks.add_task")
def create_task_on_sprint(request: HttpRequest, sprint_id: int) -> HttpResponse:

    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            # Create the task and add it to the sprint
            task_data = form.cleaned_data
            task = create_task_and_add_to_sprint(task_data, sprint_id, request.user)

            # redirect to the task details page
            return redirect("task:task-detail", task_id=task.id)

    else:
        # Render an empty form for GET requests
        form = TaskForm()

    return render(request, "tasks/task_form.html", {"form": form})


def claimed_task_view(request, task_id):
    """
    This view is for claimed ownership of task.
    """

    # asumming we have access to the user from request
    user_id = request.user.id

    try:
        claim_task(user_id, task_id)
        return JsonResponse({"message": "Task Sucessfully claimed."})

    except Task.DoesNotExist:
        return HttpResponse("Task Does Not Exist", status=status.HTTP_404_NOT_FOUND)

    except TaskAlreadyClaimedException:
        return HttpResponse(
            "Task is already Climed or Completed", status=status.HTTP_400_BAD_REQUEST
        )


@login_required
def create_sprint_view(request: HttpRequest) -> HttpResponse:
    """
    This view create a new sprint object. It takes data as name, description, start date of sprint,
    end date of sprint, validate end date after startdate through service layer, and create sprint.
    """
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")  # Ensure user is authenticated

        sprint_data = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description"),
            "start_date": request.POST.get("start_date"),
            "end_date": request.POST.get("end_date"),
        }

        # print("Request User:", request.user)  # Debug
        # print("Is Authenticated:", request.user.is_authenticated)
        # print("User Type:", type(request.user))

        sprint = create_sprint(sprint_data, creator=request.user)
        return redirect(reverse("sprint-detail", args=[sprint.id]))

    return render(request, "sprint_form.html")


def remove_task_from_sprint_view(request):
    if request.method == "POST":
        # Pass the raw request data to the service
        task_id = request.POST.get("task_id")
        sprint_id = request.POST.get("sprint_id")

        try:
            # Call the service layer
            remove_task_from_sprint(sprint_id, task_id)
            return JsonResponse(
                {
                    "success": True,
                    "message": "Task removed from the Sprint successfully.",
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse(
        {"error": "Invalid request method. Only POST is allowed."}, status=405
    )


def set_sprint_epic_view(request):
    if request.method == "POST":
        sprint_id = request.POST.get("sprint_id")
        epic_id = request.POST.get("epic_id")

        try:
            # Call the service layer
            result = set_sprint_epic(sprint_id, epic_id)
            return JsonResponse({"success": True, "message": result.get("message")})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse(
        {"error": "Invalid request method. Only POST is allowed."}, status=405
    )


def my_view(request):
    """
    Renders a template with dynamic header and footer from settings.
    Update TEMPLATE_PARTS in settings.py to change included templates.
    """
    context = {
        "header_template": settings.TEMPLATE_PARTS["header"],
        "footer_template": settings.TEMPLATE_PARTS["footer"],
    }

    return render(request, "my_template.html", context)


# view for home page of our website
def task_home(request):

    #  fetch all tasks at once
    tasks = Task.objects.filter(
        status__in=["UNASSIGNED", "IN_PROGRESS", "DONE", "ARCHIVED"]
    )

    # imnitial dictionary
    context = defaultdict(list)

    # Categorize task into their respective list
    for task in tasks:
        if task.status == "UNASSIGNED":
            context["unassigned_tasks"].append(task)
        elif task.status == "IN_PROGRESS":
            context["in_progress_tasks"].append(task)
        elif task.status == "DONE":
            context["done_tasks"].append(task)
        elif task.status == "ARCHIved":
            context["archived_tasks"].append(task)

    return render(request, "tasks/home.html", context)


# view for sprints
def sprint_list_view(request):
    # fetch all sprints
    sprints = Sprint.objects.all()
    context = {"sprints": sprints}

    return render(request, "tasks/sprints_list.html", context=context)


def sprint_details_view(request, sprint_id: Sprint):

    # Fetch the sprint object or return a 404 if it doesn't exist
    sprint = get_object_or_404(Sprint, id=sprint_id)
    context = {"sprint": sprint}

    # Render the sprint details template
    return render(request, "tasks/sprint_details.html", context)



class SprintCreateView(LoginRequiredMixin, CreateView):
    model = Sprint
    template_name = "tasks/sprint_form.html"
    form_class = SprintForm

    def get_form_kwargs(self):
        """Pass request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass the request to the form
        return kwargs

    def get_success_url(self):
        # Redirect to the detail view of the newly created Sprint object
        return reverse_lazy("tasks:sprint-detail", kwargs={"sprint_id": self.object.id})


class SprintUpdateView(UpdateView):
    model = Sprint
    template_name = "tasks/sprint_form.html"
    form_class = SprintForm

    def get_form_kwargs(self):
        """Pass request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass the request to the form
        return kwargs

    def get_object(self, queryset=None):
        """Fetch the sprint by ID."""
        return get_object_or_404(Sprint, id=self.kwargs["sprint_id"])

    def get_success_url(self):
        return reverse_lazy("tasks:sprint-detail", kwargs={"sprint_id": self.object.id})


def manage_sprint_related_to_task(request, task_pk: Task):
    task = get_task_by_id(task_pk)

    if not task:
        raise Http404("Task does not exist.")

    if request.method == "POST":
        formset = SprintFormSet(
            request.POST, queryset=get_sprint_by_task(task), request=request
        )
        if formset.is_valid():
            sprints = formset.save(commit=False)
            save_sprint_for_task(task, sprints, request.user)
            formset.save_m2m()

            return redirect("tasks:sprint-list")

    else:
        formset = SprintFormSet(queryset=get_sprint_by_task(task), request=request)

    return render(
        request, "tasks/manage_sprint.html", {"formset": formset, "task": task}
    )


class SprintDeleteView( PermissionRequiredMixin, DeleteView):
    model = Sprint
    template_name = "tasks/sprint_delete.html"
    success_url = reverse_lazy("tasks:sprint-list")
    permission_required = ("tasks.sprint_delete",)


class SprintCreateView(LoginRequiredMixin, CreateView):
    model = Sprint
    template_name = "tasks/sprint_form.html"
    form_class = SprintForm

    def get_form_kwargs(self):
        """Pass request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass the request to the form
        return kwargs

    def get_success_url(self):
        # Redirect to the detail view of the newly created Sprint object
        return reverse_lazy("tasks:sprint-detail", kwargs={"sprint_id": self.object.id})


class SprintUpdateView(UpdateView):
    model = Sprint
    template_name = "tasks/sprint_form.html"
    form_class = SprintForm

    def get_form_kwargs(self):
        """Pass request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # Pass the request to the form
        return kwargs

    def get_object(self, queryset=None):
        """Fetch the sprint by ID."""
        return get_object_or_404(Sprint, id=self.kwargs["sprint_id"])

    def get_success_url(self):
        return reverse_lazy("tasks:sprint-detail", kwargs={"sprint_id": self.object.id})


def manage_sprint_related_to_task(request, task_pk: Task):
    task = get_task_by_id(task_pk)

    if not task:
        raise Http404("Task does not exist.")

    if request.method == "POST":
        formset = SprintFormSet(
            request.POST, queryset=get_sprint_by_task(task), request=request
        )
        if formset.is_valid():
            sprints = formset.save(commit=False)
            save_sprint_for_task(task, sprints, request.user)
            formset.save_m2m()

            return redirect("tasks:sprint-list")

    else:
        formset = SprintFormSet(queryset=get_sprint_by_task(task), request=request)

    return render(
        request, "tasks/manage_sprint.html", {"formset": formset, "task": task}
    )


class SprintDeleteView( PermissionRequiredMixin, DeleteView):
    model = Sprint
    template_name = "tasks/sprint_delete.html"
    success_url = reverse_lazy("tasks:sprint-list")
    permission_required = ("tasks.sprint_delete",)



# views for Epics
def epic_list_view(request):
    # fetch all Epic
    epics = Epic.objects.all()
    context = {"epics": epics}

    return render(request, "tasks/epics_list.html", context=context)


# def epic_detail_view(request, epic_id: Epic):
#     # Fetch the sprint object or return a 404 if it doesn't exist
#     epic = get_object_or_404(Epic, id=epic_id)
#     context = {"epic": epic}

#     return render(request, "tasks/epic_detail.html", context)

class EpicDetailView(PermissionRequiredMixin, DetailView):
    model = Epic
    template_name = "tasks/epic_detail.html"
    context_object_name = "epic"
    permission_required = ("tasks.view_epic")


def manage_epic_tasks(request, epic_pk):
    # check epic is exist or not
    epic = get_epic_by_id(epic_pk)

    if not epic:
        raise Http404("Epic does not exist")

    if request.method == "POST":
        formset = EpicFormSet(request.POST, queryset=get_task_by_epic(epic))

        if formset.is_valid():
            tasks = formset.save(commit=False)
            save_task_for_epic(epic, tasks)
            formset.save_m2m  # handle many to many relationship if there are any

            return redirect("tasks:task-list")

    else:
        formset = EpicFormSet(queryset=get_task_by_epic(epic))

    return render(request, "tasks/manage_epic.html", {"formset": formset, "epic": epic})



# view for Contact form
class ContactFormView(FormView):
    template_name = "tasks/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("tasks:contact-success")

    def form_valid(self, form):
        subject = form.cleaned_data.get("subject")
        message = form.cleaned_data.get("message")
        from_email = form.cleaned_data.get("from_email")

        send_contact_email(
            subject=subject,
            message=message,
            from_email=from_email,
            to_email=["user16@gmail.com"],
        )

        return super().form_valid(form)



# custom error views

def custom_404(request, exception):
    return render(request, "404.html", {"requested_url": request.path}, status=404)


def custom_500(request):
    return render(request, "500.html", {}, status=500)


def custom_403(request, exception):
    return render(request, "403.html", {}, status=403)


class EpicCreateView( PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Epic
    template_name = "tasks/epic_form.html"
    form_class = EpicForm
    permission_required = ("tasks.add_epic",)

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:epic-detail", kwargs={"epic_id": self.object.id})
    


class EpicDeleteView(PermissionRequiredMixin, DeleteView):
    model = Epic
    template_name = "tasks/epic_delete.html"
    success_url = reverse_lazy("tasks:epic-list")
    permission_required = ("tasks.delete_epic")


class EpicUpdateView(PermissionRequiredMixin, UpdateView):
    model = Epic
    form_class = EpicForm
    template_name = "tasks/epic_form.html"
    permission_required = ("tasks.change_epic")
    
    def get_object(self, queryset = None):
        return get_object_or_404(Epic, id=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("tasks:epic-detail", kwargs={"pk": self.object.id})




