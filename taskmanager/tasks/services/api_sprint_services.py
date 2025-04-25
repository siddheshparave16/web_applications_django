from datetime import datetime
from typing import Any
from django.contrib.auth import get_user_model
from tasks.models import Sprint
from django.http import Http404


User = get_user_model()

def create_sprint(sprint_data: dict[str, Any], creator: User) -> Sprint: # type: ignore
    """
    Creates a new sprint and associates it with the given creator.

    Args:
        sprint_data (dict[str, Any]): Data for creating the sprint.
        creator (User): The user creating the sprint.

    Returns:
        Sprint: The newly created Sprint object.
    """
    # Extract dates directly (already validated by Pydantic schema)
    start_date = sprint_data["start_date"]
    end_date = sprint_data["end_date"]

    # Validate sprint end date should be after start date
    if start_date > end_date:
        raise ValueError("End date should be after Start Date")

    # Filter allowed fields and create the Sprint
    allowed_fields = {"name", "description", "start_date", "end_date"}
    sprint_data_filtered = {key: value for key, value in sprint_data.items() if key in allowed_fields}

    sprint = Sprint.objects.create(**sprint_data_filtered, creator=creator)
    return sprint


def get_sprint(sprint_id:int)-> Sprint:
    
    sprint = Sprint.objects.filter(pk=sprint_id).first()
    
    if not sprint:
        raise Http404(f"Sprint with id:{sprint_id} Does Not Exist.")
    
    return sprint


def delete_sprint(sprint_id: int):
    sprint = Sprint.objects.filter(id=sprint_id).first()

    if not sprint:
        return None
    
    deleted_sprint_data = {
        "id": sprint.id,
        "name": sprint.name,
    }
    
    sprint.delete()

    return deleted_sprint_data


def update_sprint(sprint_id: int, **sprint_data: dict):
    sprint = Sprint.objects.filter(id=sprint_id).first()

    if not sprint:
        return False
    
    for field, value in sprint_data.items():
        setattr(sprint, field, value)
    
    sprint.save()

    return True
