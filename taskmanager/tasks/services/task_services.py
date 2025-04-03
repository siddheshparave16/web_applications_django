from django.shortcuts import get_object_or_404
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from tasks.models import Task, Sprint, User
from datetime import datetime
from django.db.models import F



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


def create_task_and_add_to_sprint(task_data: dict[str,str], sprint_id: int, creator: User):
    """
    create a task and add it to a sprint
    """

    # Fetch the sprint by its ID
    sprint = Sprint.objects.get(id=sprint_id)

    # get current time and date for task
    now = datetime.now()

    # lets check is time is within sprint time
    if not sprint.start_date <= now.date() <= sprint.end_date:
        raise ValidationError("Cannot add task to sprint: current time is not within a sprint startdate and enddate")

    # transaction.atomic ensure that all operation completed successfully or not at all
    with transaction.atomic():
        # create a task
        task = Task.objects.create(
            title = task_data['title'],
            description = task_data['description'],
            creator = creator
        )

        # add the task to the sprint
        sprint.tasks.add(task)

    return task


class TaskAlreadyClaimedException(Exception):
    pass


@ transaction.atomic
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
        task = Task.objects.get(id= task_id)
        original_version = task.version

        # step 2: Check if task aready climbed orr not
        if task.owner_id:
            raise ValidationError("Task already claimed or completed.")
        
        # step 3: claimed the task
        task.status = 'IN_PROGRESS'
        task.owner = user_id
        
        # step 4: Save the task and update the version, but only if version hasn't changed
        updated_row = Task.objects.filter(id = task_id, version=original_version).update(
            status = task.status,
            owner_id = task.owner,
            version=F('version') + 1  # Increament version field
        )


        # If no rows were updated, that means another transaction changed the task
        if updated_row == 0:
            raise ValidationError("Task was updated by anathor transaction.")


    except Task.DoesNotExist:
        ValidationError('Task Does Not Exist.')


def remove_task_from_sprint(sprint_id: int, task_id: int) -> None:
    """
        This service for remove sprint from task 
    """

    try:
        sprint = Sprint.objects.get(id= sprint_id)
        task = Task.objects.get(id = task_id)

    except Sprint.DoesNotExist:
        raise ValueError("Sprint Does Not Exist.")
    except Task.DoesNotExist:
        raise ValueError("Task Does Not Exist.")
    
    # check task exist in sprint 
    if task in sprint.tasks.all():
        sprint.tasks.remove(task)
    else:
        raise ValueError("Task is not associated with the Sprint.")

