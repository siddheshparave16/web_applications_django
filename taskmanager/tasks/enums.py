from enum import Enum


class TaskStatus(str, Enum):
    """
    An enumeration representing the possible statuses of a task.

    Attributes:
        UNASSIGNED: The task has not been assigned to anyone.
        IN_PROGRESS: The task is currently being worked on.
        DONE: The task has been completed.
        ARCHIVED: The task has been archived and is no longer active.
    """

    UNASSIGNED = "UNASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    ARCHIVED = "ARCHIVED"
