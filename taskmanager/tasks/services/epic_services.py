from tasks.models import Task, Epic


# Service for get epic from epic_id
def get_epic_by_id(epic_id: Epic) -> Epic|None:
    return Epic.objects.filter(pk=epic_id).first()


# service from fetch all task related to epic
def get_task_by_epic(epic: Epic) -> list[Task]:
    return Task.objects.filter(epic= epic)


# service for save task for epic
def save_task_for_epic(epic:Epic, tasks: list[Task]):
    for task in tasks:
        task.save()
        task.epic = epic



