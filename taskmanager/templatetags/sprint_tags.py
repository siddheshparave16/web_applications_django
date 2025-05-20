from django import template
from django.db.models import Count
from tasks.models import Sprint

"""
This file defines custom template tags for use in Django templates.

Custom template tags allow you to implement custom logic that can be invoked
directly within your HTML templates to enhance their functionality.

"""

register = template.Library()


@register.simple_tag
def task_summary(sprint: Sprint) -> dict:
    # Group tasks by status and count each group
    task_counts = (
        sprint.tasks.values("status").annotate(count=Count("status")).order_by()
    )

    # Convert the result into a dictionary: {status: count}
    summary = {item["status"]: item["count"] for item in task_counts}

    return summary


@register.simple_tag
def task_priority_summary(sprint: Sprint) -> dict:
    """
    Custom template tag to summarize tasks by priority for a given sprint.

    Args:
        sprint (Sprint): The Sprint instance whose tasks will be summarized.

    Returns:
        dict: A dictionary where the keys are priority levels ('HIGH', 'MEDIUM', 'LOW')
            and the values are the count of tasks with that priority.

    Example Output:
        {
            "HIGH": 7,
            "MEDIUM": 9,
            "LOW": 4
        }
    """

    # Group task by Priority and count each group
    task_by_priority_count = (
        sprint.tasks.values("priority").annotate(count=Count("priority")).order_by()
    )

    priority_summary = {
        item["priority"]: item["count"] for item in task_by_priority_count
    }

    return priority_summary
