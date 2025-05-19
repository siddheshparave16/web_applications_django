from django.contrib.auth.models import User
from tasks.models import Sprint, Epic
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime


def create_sprint(sprint_data: dict[str, str], creator: User) -> Sprint:
    """
    Creates a new sprint and associates it with the given creator.

    Args:
        sprint_data (dict[str, Any]): Data for creating the sprint, e.g., name, description, dates.
        creator (User): The user creating the sprint.

    Returns:
        Sprint: The newly created Sprint object.
    """

    # Convert string dates to datetime.date objects
    start_date = datetime.strptime(sprint_data['start_date'], "%Y-%m-%d").date()
    end_date = datetime.strptime(sprint_data['end_date'], "%Y-%m-%d").date()

    
    # Validate sprint end date should be after start date
    if start_date > end_date:
        raise ValueError("End date should be after Start Date")

    sprint = Sprint.objects.create(**sprint_data, creator = creator)            # Assuming 'created_by' is the field in Sprint model

    return sprint



def set_sprint_epic(sprint_id: int, epic_id: int) -> dict:
    """
        Associates a Sprint with an Epic, ensuring that the Epic's creation date
        is before the Sprint's start date.

        Args:
            sprint_id (int): The ID of the Sprint.
            epic_id (int): The ID of the Epic.

        Returns:
            dict: Success message indicating the Sprint was added to the Epic.

        Raises:
            ValueError: If the Sprint or Epic does not exist.
            ValidationError: If the Epic's creation date is after the Sprint's start date.
    """
     
    try:
        sprint = Sprint.objects.get(id= sprint_id)
        epic = Epic.objects.get(id= epic_id)
    except Sprint.DoesNotExist:
        raise ValueError("Sprint Does Not Exist.")
    except Epic.DoesNotExist:
        raise ValueError("Epic Does Not Exist.")
    
    if not epic.created_at <= sprint.start_date:
        raise ValidationError(
                f"Epic's creation date ({epic.created_at.date()}) must be before the Sprint's start date ({sprint.start_date})."
            )

    # Add the Sprint to the Epic
    with transaction.atomic():
        epic.sprints.add(sprint)        # Add the sprint to the epic's ManyToManyField
        epic.save()                     # Save changes to ensure consistency

        return {"success": True, "message": f"Sprint '{sprint.name}' successfully added to Epic '{epic.name}'."}
