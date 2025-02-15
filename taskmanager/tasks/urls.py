from django.urls import path
from django.views.generic import TemplateView

app_name = 'tasks'              # this is for namespacing the urls

urlpatterns = [
    path('', TemplateView.as_view(template_name='tasks/home.html'), name='home'),
    path('help/', TemplateView.as_view(template_name='tasks/help.html'), name='help'),
    path('about/', TemplateView.as_view(template_name='tasks/about.html'), name='about')
    
]
