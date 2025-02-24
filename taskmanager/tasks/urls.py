from django.urls import path, register_converter
from django.views.generic import TemplateView
from .views import TaskListView, TaskDetailView, TaskCreateView, TaskUpdateView, TaskDeleteView, create_task_on_sprint
from . import views, converters


app_name = 'tasks'            # namespace - this is for namespacing the urls

register_converter(converters.DateConverter, 'yyyymmdd')    # register the custom converter


urlpatterns = [
    path('', TemplateView.as_view(template_name='tasks/home.html'), name='home'),
    path('help/', TemplateView.as_view(template_name='tasks/help.html'), name='help'),
    path('about/', TemplateView.as_view(template_name='tasks/about.html'), name='about'),
    path('tasks/', TaskListView.as_view(), name = 'task-list'),                         # Get - all tasks
    path('tasks/new/', TaskCreateView.as_view(), name='task-create'),                   # POST - Create a new task
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),              # GET - Retrieve a task
    path('tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='task-update'),         # PUT/PAT0CH - Update a task
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),       # DELETE - Delete a task
    path('tasks/sprint/add/<int:pk>/', create_task_on_sprint, name='task-add-to-sprint'),
]

# custom errors handler
handler404 = 'tasks.views.custom_404'
handler500 = 'tasks.views.custom_500'


