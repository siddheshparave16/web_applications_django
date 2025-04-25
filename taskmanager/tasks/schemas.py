from ninja import ModelSchema, Schema, FilterSchema
from .models import Task, Sprint, Epic
from pydantic import Field, model_validator
import datetime
from typing import Optional
from tasks.enums import TaskStatus

"""
class TaskSchemaIn(Schema):
    title: str
    description: str

    """


class CreateSchemaOut(Schema):
    id: int

    class Config:
        description = "Schema for the created object output"


class TaskSchemaIn(ModelSchema):
    class Config:
        model = Task
        model_fields = ["title", "description"]
        model_field_optional = ["status"]
        description = "Schema for creating a new task"


class TaskSchemaOut(ModelSchema):
    # owner: UserSchema | None = Field(None)
    class Config:
        model = Task
        model_fields = ["title", "description"]


class PathDate(Schema):
    year: int = Field(..., ge=1)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)

    def value(self):
        return datetime.date(self.year, self.month, self.day)

    @model_validator(mode="after")
    def validate_date(self) -> "PathDate":
        try:
            datetime.date(self.year, self.month, self.day)
        except ValueError:
            raise ValueError(
                "The date {self.year}-{self.month}-{self.day} is not valid."
            )

        return self


class TaskFilterSchema(FilterSchema):
    title: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskIdInput(Schema):
    task_id: int = Field(..., ge=1, description="Task Id must be positive integer.")

    # Add custom validation logic
    @model_validator(mode="after")
    def validate_task_id(cls, values):
        task_id = values.task_id
        if task_id <= 0:
            raise ValueError(f"The task_id {task_id} must be a positive integer.")
        return values


class SprintSchemaOut(ModelSchema):
    class Config:
        model = Sprint
        model_fields = ["name", "description", "start_date", "end_date", "tasks"]


class SprintIdInput(Schema):
    sprint_id: int = Field(..., ge=1, description="Sprint Id must be positive input")


class SprintCreateSchemaIn(ModelSchema):
    class Config:
        model = Sprint
        model_fields = ["name", "description", "start_date", "end_date"]


class ErrorResponse(Schema):
    detail: str


class SuccessResponse(Schema):
    detail: str
    

class EpicSchemaOut(ModelSchema):
    class Config:
        model = Epic
        model_fields = ["name", "description"]


class EpicIdInput(Schema):
    epic_id: int = Field(..., ge=1, description="Epic Id must be positive input")


class EpicSchemaIn(ModelSchema):
    class Config:
        model = Epic
        model_fields = ["name", "description"]
        description = "Schema for creating a new Epic"