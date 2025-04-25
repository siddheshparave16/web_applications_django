from ninja import Router, Path, Query
from tasks.models import Task
from tasks.schemas import (
    TaskSchemaIn,
    TaskSchemaOut,
    CreateSchemaOut,
    PathDate,
    TaskFilterSchema,
    TaskIdInput,
    SuccessResponse,
    ErrorResponse
)
from django.http import HttpRequest, HttpResponse, Http404, JsonResponse
from http import HTTPStatus
from tasks.services import task_services
from ninja.pagination import paginate
from tasks.enums import TaskStatus
from ninja.errors import HttpError
from django.core.exceptions import ValidationError
from accounts.api.security import required_permission
from django_ratelimit.decorators import ratelimit


router = Router(tags=["tasks"])

# @router.get("/")
# def list_tasks(request):
#     return {"results": [
#         {"id":1, "title": "test title"},
#         ]}


@router.get("/", response=list[TaskSchemaOut])
@paginate  # allow setting the limit and offset by passing into URL parameter limit and offset
@required_permission("tasks.view_task")
def list_tasks(request, filters: TaskFilterSchema = Query(None)):
    """
    API endpoint to retrieve tasks with optional filters.

    Query Parameters:
        - title: Partial case-insensitive match for task title.
        - status: Exact match for task status.

    Returns:
        Paginated list of tasks.
    """
    return task_services.list_tasks(title=filters.title, status=filters.status)


@router.post("/", response={201: CreateSchemaOut})
@required_permission("tasks.add_task")
@ratelimit(key="ip", rate="10/h")
def create_task(request: HttpRequest, task_in: TaskSchemaIn):
    creator = request.user
    return task_services.create_task(creator=creator, **task_in.dict())


@router.get("/{int:task_id}", response=TaskSchemaOut)
@required_permission("tasks.view_task")
def get_task(request: HttpRequest, task_id: TaskIdInput):

    task = task_services.get_task(task_id=task_id.task_id)

    if not task:
        raise Http404("Task Not Found")

    return task


@router.put("/{int:task_id}")
@required_permission("tasks.change_task")
def update_task(request: HttpRequest, task_id: int, task_data: TaskSchemaIn):
    was_updated_task = task_services.update_task(task_id, **task_data.dict())

    if not was_updated_task:
        return JsonResponse({"detail": "Task Not Found"}, status=HTTPStatus.NOT_FOUND)

    return HttpResponse(status=HTTPStatus.NO_CONTENT)


@router.delete("/{int:task_id}")
@required_permission("tasks.delete_task")
def delete_task(request: HttpRequest, task_id: int):
    task_services.delete_task(task_id)
    return HttpResponse(status=HTTPStatus.NO_CONTENT)


@router.get("/archive/{year}/{month}/{day}", response=list[TaskSchemaOut])
@paginate
@required_permission("tasks.view_task")
def archive_task(request: HttpRequest, created_at: PathDate = Path(...)):
    """
    Retrieve archived tasks for a specific date.

    Fetches tasks that were archived on the specified year, month, and day,
    with results paginated.

    Args:
        request (HttpRequest): The HTTP request object.
        created_at (PathDate): Date parameters (year, month, day) from the URL.

    Returns:
        List[TaskSchemaOut]: Paginated list of archived tasks.

    Example:
        GET /archive/2025/3/20
    """
    return task_services.search_task(
        created_at=created_at.value(), status=TaskStatus.ARCHIVED.value
    )


@router.get("/error")
def generate_error(request):
    raise HttpError(status_code=404, message="Custom error Message")


@router.post("/{task_id}/claim/", 
             response={200: SuccessResponse, 500: ErrorResponse, 404: ErrorResponse, 403: ErrorResponse}
             )
@required_permission("task.change_task")
def claim_task_endpoint(request: HttpRequest, task_id: int):
    """
        API endpoint to claim a task.
    """
    user = request.user

    try:
        claimed_task_sucess = task_services.claim_task(task_id, user)
        return 200, {"detail": f"Task Succesfully claimed by {user.username}"}
    except Http404 as e:
        return 404, {"detail": str(e)}
    except PermissionError as e:
        return 403, {"detail": str(e)}
    except Exception as e:
        return 500, {"detail": "An unexpected error occurred"}


    
    