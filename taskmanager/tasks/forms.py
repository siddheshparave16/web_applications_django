from django import forms
from tasks.models import Task, SubscribedEmail, Formsubmission, Sprint, Epic
from tasks.fields import EmailsListField
from django.forms import modelformset_factory, BaseModelFormSet
from uuid import uuid4
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from uuid import uuid4
from .models import Task, Formsubmission, SubscribedEmail


class TaskForm(forms.ModelForm):
    uuid = forms.UUIDField(required=False, widget=forms.HiddenInput())
    watchers = EmailsListField(required=False)

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "watchers",
            "file_upload",
            "image_upload",
        ]
        exclude = ["creator"]  # Exclude the creator field from the form

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

        # Check if an instance is provided and populate watchers field
        if self.instance and self.instance.pk:
            self.fields["watchers"].initial = ", ".join(
                email.email for email in self.instance.watchers.all()
            )

        # Initialize new UUID for form creation
        self.fields["uuid"].initial = uuid4()

    def clean_uuid(self):
        uuid_value = self.cleaned_data.get("uuid")

        with transaction.atomic():
            try:
                # Try to record the form submission by UUID
                Formsubmission.objects.create(uuid=uuid_value)
            except IntegrityError:
                # The UUID already exists, so the form was already submitted
                raise ValidationError("This form has already been submitted")

        return uuid_value

    def save(self, commit=True):
        # First, save the Task instance
        task = super().save(commit)

        # If commit is True, save the associated emails
        if commit:
            # First, remove old emails associated with the task
            task.watchers.all().delete()

            # Add the new emails to the Email Model
            for email_str in self.cleaned_data["watchers"]:
                SubscribedEmail.objects.create(email=email_str, task=task)

        return task


"""
# TaskForm using Redis

class TaskFormWithRedis(forms.ModelForm):
    uuid = forms.UUIDField(required=False, widget=forms.HiddenInput())
    watchers = EmailsListField(required=False)
    
    class Meta:
        model = Task                            # model attribute specifies which django model the form is linked to
        fields = ['title', 'description', 'status', 'watchers', 'file_upload', 'image_upload']         # list of model fields want to include in form for display and validate


    def __init__(self, *args, **kwargs):

        super(TaskForm, self).__init__(*args, **kwargs)

        # check if an Instance is provided and populate watchers field
        if self.instance and self.instance.pk:
            self.fields['watchers'].initial = ', '.join(email.email for email in self.instance.watchers.all()) 
        
        # initialize new uuid for form creation
        self.fields['uuid'].initial = uuid4()

    def clean_uuid(self):
        uuid_value = self.cleaned_data.get('uuid')

        was_set = cache.set(uuid_value, "submitted", nx=True)

        if not was_set:
            # if 'was_set' is false, the UUID already exists in the cache. 
            # this indicated the duplicate form submission
            
            raise ValidationError("This form has already been submitted.")
        
        return uuid_value

"""


class ContactForm(forms.Form):
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    from_email = forms.EmailField(required=True)


EpicFormSet = modelformset_factory(Task, form=TaskForm, extra=0)


class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ["name", "description", "start_date", "end_date"]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "text", "class": "datepicker"}, format="%Y-%m-%d"
            ),
            "end_date": forms.DateInput(
                attrs={"type": "text", "class": "datepicker"}, format="%Y-%m-%d"
            ),
        }

    def __init__(self, *args, **kwargs):
        # extract the user object
        self.request = kwargs.pop("request", None)  # Extract request
        super().__init__(*args, **kwargs)

        # Ensure dates are properly formatted for the initial data
        if self.initial.get("start_date"):
            self.fields["start_date"].widget.attrs["value"] = self.initial[
                "start_date"
            ].strftime("%Y-%m-%d")
        if self.initial.get("end_date"):
            self.fields["end_date"].widget.attrs["value"] = self.initial[
                "end_date"
            ].strftime("%Y-%m-%d")

    def clean(self):
        cleaned_data = super().clean()

        name = self.cleaned_data.get("name")

        if not name:
            raise forms.ValidationError("Name is required.")

        if not self.request or not self.request.user.is_authenticated:
            raise forms.ValidationError("You must be logged in to create a sprint.")

        return cleaned_data

    def save(self, commit=True):
        # Get the instance but don't save it to the database yet
        sprint = super().save(commit=False)

        if self.request:
            sprint.creator = self.request.user

        # Save to the database only if commit is True
        if commit:
            sprint.save()

        return sprint


class BaseSprintFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)  # Extract request
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        """Pass request to each form inside the formset"""
        kwargs["request"] = self.request  # Pass request to each form
        return super()._construct_form(i, **kwargs)


# ModelFormSet for Sprints
SprintFormSet = modelformset_factory(
    Sprint, form=SprintForm, formset=BaseSprintFormSet, extra=0
)

class EpicForm(forms.ModelForm):
    class Meta:
        model = Epic
        fields = ["name", "description"]

