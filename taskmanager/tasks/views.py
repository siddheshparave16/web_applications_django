from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .maxins import SprintTaskWithinRangeMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from .services import task_services
from .services.task_services import create_task_and_add_to_sprint, claim_task, TaskAlreadyClaimedException, remove_task_from_sprint
from .services.sprint_services import create_sprint, set_sprint_epic
from tasks.models import Task, Sprint, Epic
from rest_framework import status
from django.conf import settings
from collections import defaultdict




# Create your views here.

class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task_details.html'
    context_object_name = 'task'

class TaskCreateView(SprintTaskWithinRangeMixin, CreateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'start_date', 'end_date']

    def get_success_url(self):
        return reverse_lazy('tasks:task-details', kwargs={"pk": self.object.id})
    

class TaskUpdateView(SprintTaskWithinRangeMixin, UpdateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'start_date', 'end_date']

    def get_sucess_url(self):
        return reverse_lazy('tasks:task-details', kwargs={"pk": self.object.id})
    

class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task-list')


# function based view
def check_task(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # extract the task_id parameter from post date
        task_id = request.POST.get('task_id')

        if task_services.check_task(task_id):
            return HttpResponseRedirect(reverse("sucess"))
        
        if task_id:
            return HttpResponseRedirect(reverse("sucess"))
        else:
            # If task_id is not provided, re-render the form with an error message
            return render(request, "add_task_to_sprint.html", {"error": "Task ID is required"})
    else:
        # if request method is not post just render the form
        return render(request, 'tasks/check_task.html')



def create_task_on_sprint(request: HttpRequest, sprint_id: int) -> HttpResponse:

    if request.method == 'POST':

        task_data: dict[str, str] = {
            'title': request.POST.get['title'],
            'description': request.POST.get['description'],
            'status': request.POST.get['status', 'UNASSINGED']
        }


        task = create_task_and_add_to_sprint(task_data, sprint_id, request.user)

        return redirect('task-details', task_id = task.id)
    
    raise Http404('Not Found')


def claimed_task_view(request, task_id):
    """
    This view is for claimed ownership of task.
    """
    
    # asumming we have access to the user from request
    user_id = request.user.id

    try:
        claim_task(user_id, task_id)
        return JsonResponse({'message': 'Task Sucessfully claimed.'})

    except Task.DoesNotExist:
        return HttpResponse("Task Does Not Exist", status= status.HTTP_404_NOT_FOUND)
    
    except TaskAlreadyClaimedException:
        return HttpResponse("Task is already Climed or Completed", status= status.HTTP_400_BAD_REQUEST)


def create_sprint_view(request: HttpRequest) -> HttpResponse:
    """
        This view create a new sprint object. It takes data as name, description, start date of sprint,
        end date of sprint, validate end date after startdate through service layer, and create sprint.
    """
    if request.method == 'POST':
        sprint_data = {
            'name': request.POST.get['name'],
            'description': request.POST.get['description'],
            'start_date': request.POST.get['start_date'],
            'end_date': request.POST.get['end_date']
        }

        sprint = create_sprint(sprint_data)

        return redirect(request, 'sprint_details.html', sprint.id)

    else:
        # Render an empty form for creating a sprint
        return render(request, 'sprint_form.html')


def remove_task_from_sprint_view(request):
    if request.method == 'POST':
        # Pass the raw request data to the service
        task_id = request.POST.get('task_id')
        sprint_id = request.POST.get('sprint_id')

        try:
            # Call the service layer
            remove_task_from_sprint(sprint_id, task_id)
            return JsonResponse({'success': True, 'message': 'Task removed from the Sprint successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)


def set_sprint_epic_view(request):
    if request.method == 'POST':
        sprint_id = request.POST.get('sprint_id')
        epic_id = request.POST.get('epic_id')

        try:
            # Call the service layer
            result = set_sprint_epic(sprint_id, epic_id)
            return JsonResponse({'success': True, 'message': result.get('message')})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        
    return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)


def my_view(request):
    context = {
        "header_template": settings.TEMPLATE_PARTS["header"],
        "footer_template": settings.TEMPLATE_PARTS["footer"]
    }

    return render(request, "my_template.html", context)


# view for home page of our website

def task_home(request):

    #  fetch all tasks at once
    tasks = Task.objects.filter(status__in = ['UNASSIGNED', 'IN_PROGRESS', 'DONE', 'ARCHIVED'])

    # imnitial dictionary
    context = defaultdict(list)

    # Categorize task into their respective list
    for task in tasks:
        if task.status == "UNASSIGNED":
            context['unassigned_tasks'].append(task)
        elif task.status == "IN_PROGRESS":
            context['in_progress_tasks'].append(task)
        elif task.status == "DONE":
            context['done_tasks'].append(task)
        elif task.status == "ARCHIved":
            context['archived_tasks'].append(task)


    return render(request, "tasks/home.html", context)


# view for sprints
def sprint_list_view(request):
    # fetch all sprints
    sprints = Sprint.objects.all()
    context = {'sprints': sprints}

    return render(request, 'tasks/sprints_list.html', context=context)


def sprint_details_view(request, sprint_id: Sprint):

    # Fetch the sprint object or return a 404 if it doesn't exist
    sprint = get_object_or_404(Sprint, id=sprint_id)
    context = {'sprint': sprint}

    # Render the sprint details template
    return render(request, 'tasks/sprint_details.html', context)


# views for Epics
def epic_list_view(request):
    # fetch all Epic
    epics = Epic.objects.all()
    context = {'epics': epics}

    return render(request, 'tasks/epics_list.html', context=context)


def epic_detail_view(request,epic_id:Epic):
    # Fetch the sprint object or return a 404 if it doesn't exist
    epic = get_object_or_404(Epic, id=epic_id)
    context = {'epic': epic}

    return render(request, 'tasks/epic_detail.html', context)


# custom error views 

def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)

def custom_500(request, exception):
    return render(request, '500.html', {}, status=500)





