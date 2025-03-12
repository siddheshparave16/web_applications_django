from django.http import HttpResponseBadRequest, Http404
from .services.task_services import can_add_task_to_sprint


class SprintTaskWithinRangeMixin:
    """
        Mixin to ensure a task being created or updated is within the 
        date range of its associated sprint
    """

    def dispatch(self, request, *args, **kwargs):
        # Handle the object for UpdateView, and None for CreateView
        task = None
        if hasattr(self, 'get_object'):
            try:
                task = self.get_object()
            except (AttributeError, Http404):
                task = None

        sprint_id = request.POST.get('sprint')

        if sprint_id:
            # If a task exists (for UpdateView) or it about to created( for CreateView)
            if task or request.method == "POST":
                if not can_add_task_to_sprint(task, sprint_id):
                    return HttpResponseBadRequest(
                        " task creation date is outside the date range of the associated sprint."
                        )
        
        # Proceed with normal request handling
        return super().dispatch(request, *args, **kwargs)
            
