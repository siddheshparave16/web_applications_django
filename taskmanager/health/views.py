from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def liveness(request):
    return JsonResponse({"status": "ok"})

@csrf_exempt
def readiness(request):
    return JsonResponse({"status": "ready"})
