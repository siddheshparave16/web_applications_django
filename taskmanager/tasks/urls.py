from django.urls import path, register_converter
from django.views.generic import TemplateView
from .views import (TaskListView, TaskDetailView, TaskCreateView, TaskUpdateView, TaskDeleteView,
                    create_task_on_sprint, task_home, sprint_list_view, sprint_details_view, 
                    epic_list_view, epic_detail_view, ContactFormView, manage_epic_tasks, SprintFormView, SprintUpdateView,
                    manage_sprint_related_to_task)

from . import views, converters
from django.conf import settings
from django.conf.urls.static import static


app_name = 'tasks'            # namespace - this is for namespacing the urls

register_converter(converters.DateConverter, 'yyyymmdd')    # register the custom converter


urlpatterns = [
    path('', task_home, name='home'),
    path('help/', TemplateView.as_view(template_name='tasks/help.html'), name='help'),
    path('about/', TemplateView.as_view(template_name='tasks/about.html'), name='about'),
    path('tasks/', TaskListView.as_view(), name = 'task-list'),                         # Get - all tasks
    path('tasks/new/', TaskCreateView.as_view(), name='task-create'),                   # POST - Create a new task
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),              # GET - Retrieve a task
    path('tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='task-update'),         # PUT/PATCH - Update a task
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),       # DELETE - Delete a task
    path('tasks/sprint/add/<int:pk>/', create_task_on_sprint, name='task-add-to-sprint'),

    # sprints view
    path('sprints/', sprint_list_view, name='sprint-list'),
    path('sprints/<int:sprint_id>/', sprint_details_view, name='sprint-detail'),
    path('sprints/new/', SprintFormView.as_view(), name='sprint-create'),
    path('sprints/<int:sprint_id>/edit/', SprintUpdateView.as_view(), name='sprint-update'),

    # epics view
    path('epics/', epic_list_view, name='epic-list'),
    path('epics/<int:epic_id>/', epic_detail_view, name='epic-detail'),

    # ContactForm view
    path('contact/',ContactFormView.as_view(), name='contact' ),
    path('contact-success/', TemplateView.as_view(template_name='tasks/contact_success.html'), name='contact-success'),

    # view for formset
    path("epic/<int:epic_pk>/", manage_epic_tasks, name='task-batch-create'),
    path('task/<int:task_pk>/', manage_sprint_related_to_task,  name='sprint-batch-create')

] 

if settings.DEBUG:
    # allow serving uploaded media using development server
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# custom errors handler
handler404 = 'tasks.views.custom_404'
handler500 = 'tasks.views.custom_500'


