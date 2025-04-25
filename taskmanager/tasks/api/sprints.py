from ninja import Router
from tasks.schemas import SprintSchemaOut, SprintCreateSchemaIn, SprintIdInput, CreateSchemaOut
from ninja.pagination import paginate
from tasks.models import Sprint
from tasks.services import api_sprint_services
from django.http import HttpRequest, JsonResponse, HttpResponse
from http import HTTPStatus


router = Router(tags=["sprints"])


@router.get("/", response=list[SprintSchemaOut])
@paginate
def sprint_list(request):
    # return {"results": [{"id":sprint.id, "name": sprint.name} for sprint in Sprint.objects.all()]}
    return Sprint.objects.all()


@router.post("/", response=CreateSchemaOut)
def create_sprint(request, sprint_in:SprintCreateSchemaIn):
    creator = request.user
    return api_sprint_services.create_sprint(sprint_in.dict(), creator=creator)


@router.get("/{sprint_id}", response=SprintSchemaOut)
def get_sprint(request, sprint_id: SprintIdInput):
    return api_sprint_services.get_sprint(sprint_id.sprint_id)


@router.put("/{sprint_id}")
def update_sprint(request:HttpRequest, sprint_id:int, sprint_data: SprintCreateSchemaIn):
    
    was_updated_sprint = api_sprint_services.update_sprint(sprint_id, **sprint_data.dict())

    if not was_updated_sprint:
        return JsonResponse({"details":f"Sprint Not found."}, status= HTTPStatus.NOT_FOUND)
    

    return HttpResponse(status= HTTPStatus.NO_CONTENT)


@router.delete("/{sprint_id}", response={200: dict, 404: dict})
def delete_sprint(request, sprint_id: int):
    result =  api_sprint_services.delete_sprint(sprint_id)

    if result is None:
        return 404, {"error": f"Sprint with id {sprint_id} does not exist."}
    
    return 200, {
        "message":"Sprint deleted successfully",
        "sprint":result,
    }


