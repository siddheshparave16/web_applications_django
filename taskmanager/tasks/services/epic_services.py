from tasks.models import Task, Epic
from django.contrib.auth import get_user_model
from django.http import Http404

User = get_user_model()

# Service for get epic from epic_id
def get_epic_by_id(epic_id: Epic) -> Epic | None:
    return Epic.objects.filter(pk=epic_id).first()


# service from fetch all task related to epic
def get_task_by_epic(epic: Epic) -> list[Task]:
    return Task.objects.filter(epic=epic)


# service for save task for epic
def save_task_for_epic(epic: Epic, tasks: list[Task]):
    for task in tasks:
        task.save()
        task.epic = epic


def create_epic(creator: User, **epic_data: any): # type: ignore
    epic = Epic(**epic_data)
    epic.creator = creator
    epic.save()

    return epic


def update_epic(epic_id: int, **epic_data: any):
    epic = Epic.objects.filter(pk=epic_id).first()

    if not epic:
        return False
    
    for field, value in epic_data.items():
        setattr(epic, field, value)

    epic.save()

    return True


def delete_epic(epic_id):
    epic = Epic.objects.filter(pk=epic_id).first()

    if not epic:
        return False
    
    epic.delete()
    return True

    

