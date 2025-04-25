from django.shortcuts import get_object_or_404
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from tasks.models import Task, Sprint, User
from datetime import datetime, date
from django.db.models import F
from tasks.enums import TaskStatus
from django.http import Http404



# create a new task
def create_task(creator: User, **task_data: any):
    task = Task(**task_data)
    task.creator = creator
    task.save()
    return task


# list of all task
def list_tasks(title: str | None = None, status: str | None = None):
    """
    Retrieve tasks filtered by title and/or status, or return all tasks if no filters are provided.

    Args:
        title (str | None): Task title to filter by.
        status (str | None): Task status to filter by.

    Returns:
        Queryset of tasks matching the filter criteria, or all tasks if no filters are provided.
    """

    filters = {}

    if title:
        filters["title__icontains"] = title

    if status:
        filters["status"] = status.upper()

    return Task.objects.filter(**filters)


def get_task(task_id: int) -> Task | None:
    task = Task.objects.select_related("owner", "creator").filter(pk=task_id).first()
    return task


def update_task(task_id: int, **task_data: dict):
    task = Task.objects.filter(pk=task_id).first()

    if not task:
        return False

    # Iterate over the task data and set the attributes on the task instance
    for field, value in task_data.items():
        setattr(task, field, value)

    # Save the task instance, which applies the updates to the database
    task.save()

    return True


def delete_task(task_id: int):
    task = Task.objects.filter(pk=task_id).first()
    if not task:
        return

    task.delete()


def search_task(created_at: date, status: TaskStatus):
    tasks = Task.objects.filter(created_at__date=created_at, status=status).order_by(
        "status", "created_at"
    )
    print(tasks)
    return tasks


def can_add_task_to_sprint(task, sprint_id):
    """
    check if a task can be added to a sprint
    """

    sprint = get_object_or_404(Sprint, sprint_id)

    return sprint.start_date <= task.created_at.date() <= sprint.end_date


def check_task(task_id):
    """
    Check if a task exists
    """

    return Task.objects.filter(pk=task_id).exists()


def create_task_and_add_to_sprint(
    task_data: dict[str, str], sprint_id: int, creator: User
):
    """
    create a task and add it to a sprint
    """

    # Fetch the sprint by its ID
    sprint = Sprint.objects.get(id=sprint_id)

    # get current time and date for task
    now = datetime.now()

    # lets check is time is within sprint time
    if not sprint.start_date <= now.date() <= sprint.end_date:
        raise ValidationError(
            "Cannot add task to sprint: current time is not within a sprint startdate and enddate"
        )

    # transaction.atomic ensure that all operation completed successfully or not at all
    with transaction.atomic():
        # create a task
        task = Task.objects.create(
            title=task_data["title"],
            description=task_data["description"],
            creator=creator,
        )

        # add the task to the sprint
        sprint.tasks.add(task)

    return task


class TaskAlreadyClaimedException(Exception):
    pass


@transaction.atomic
def claim_task(user_id: int, task_id: int) -> None:

    # lock the task row to prevent other transactions from claiming it simultaneously
    task = Task.objects.select_for_update.get(id=task_id)

    # check id task already climed
    if task.owner_id:
        raise TaskAlreadyClaimedException("Task already claimed or completed.")

    # climed the task
    task.status = "IN_PROGRESS"
    task.owner_id = user_id
    task.save()


def claim_task_optimistically(user_id: int, task_id: int) -> None:
    try:
        # step 1: Read the task and its version
        task = Task.objects.get(id=task_id)
        original_version = task.version

        # step 2: Check if task aready climbed orr not
        if task.owner_id:
            raise ValidationError("Task already claimed or completed.")

        # step 3: claimed the task
        task.status = "IN_PROGRESS"
        task.owner = user_id

        # step 4: Save the task and update the version, but only if version hasn't changed
        updated_row = Task.objects.filter(id=task_id, version=original_version).update(
            status=task.status,
            owner_id=task.owner,
            version=F("version") + 1,  # Increament version field
        )

        # If no rows were updated, that means another transaction changed the task
        if updated_row == 0:
            raise ValidationError("Task was updated by anathor transaction.")

    except Task.DoesNotExist:
        ValidationError("Task Does Not Exist.")


def remove_task_from_sprint(sprint_id: int, task_id: int) -> None:
    """
    This service for remove sprint from task
    """

    try:
        sprint = Sprint.objects.get(id=sprint_id)
        task = Task.objects.get(id=task_id)

    except Sprint.DoesNotExist:
        raise ValueError("Sprint Does Not Exist.")
    except Task.DoesNotExist:
        raise ValueError("Task Does Not Exist.")

    # check task exist in sprint
    if task in sprint.tasks.all():
        sprint.tasks.remove(task)
    else:
        raise ValueError("Task is not associated with the Sprint.")


def claim_task(task_id: int, user: User):
    """
    Service to claim a task by a user.
    """

    if not user and not isinstance(user, User):
        raise PermissionError("Authentication Required.")
    
    task = Task.objects.filter(id=task_id).first()

    if not task:
        raise Http404("Task Does Not Exist.")
    
    if task.owner:
        raise PermissionError("The Task is already claimed.")
    
    task.owner = user
    task.save()

    return True