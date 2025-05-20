from ninja import Router
from tasks.models import Epic
from tasks.schemas import EpicSchemaOut, EpicIdInput, EpicSchemaIn, CreateSchemaOut
from ninja.pagination import paginate
from django.http import HttpRequest, Http404, JsonResponse, HttpResponse
from tasks.services import epic_services
from http import HTTPStatus



router = Router(tags= ["epics"])


@router.get("/", response=list[EpicSchemaOut])
@paginate
def list_epic(request):
    return Epic.objects.all()

@router.get("/{int:epic_id}", response=EpicSchemaOut)
def get_epic(request: HttpRequest, epic_id:EpicIdInput):
    """
    In the get_epic_by_id function, the parameter epic_id is automatically parsed into an EpicIdInput object by Django Ninja. 
    This object contains the field epic_id.
    """
    epic = epic_services.get_epic_by_id(epic_id=epic_id.epic_id)

    if not epic:
        raise Http404(f"the Epic {epic_id} does not exist.")
    
    return epic


@router.post("/", response=CreateSchemaOut)
def create_epic(request, epic_in: EpicSchemaIn):
    creator = request.user
    return epic_services.create_epic(creator=creator, **epic_in.dict())


@router.put("/{int:epic_id}", response={201: EpicSchemaOut})
def update_epic(request, epic_id:EpicIdInput, epic_in:EpicSchemaIn):
    was_updated_epic = epic_services.update_epic(epic_id.epic_id, **epic_in.dict())

    if not was_updated_epic:
        return JsonResponse({"detail": f"Epic id:{epic_id.epic_id} not Found"}, status= HTTPStatus.NOT_FOUND)
    
    return HttpResponse(status=HTTPStatus.NO_CONTENT)


@router.delete("/{int:epic_id}")
def delet_epic(request, epic_id:EpicIdInput):
    was_deleted_epic = epic_services.delete_epic(epic_id=epic_id.epic_id)

    if not was_deleted_epic:
        return JsonResponse({"detail": f"Epic id:{epic_id.epic_id} not found"}, status= HTTPStatus.NOT_FOUND)

    return JsonResponse({"detail": f"Epic id:{epic_id.epic_id} delete successfully."}, status= HTTPStatus.OK)