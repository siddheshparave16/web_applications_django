from ninja import NinjaAPI
from tasks.api.tasks import router as tasks_router
from tasks.api.sprints import router as sprint_router
from tasks.api.epics import router as epic_router
from accounts.api.views import router as account_router
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
from accounts.api.security import ApiAuthToken, JWTAuth
from django_ratelimit.exceptions import Ratelimited


api = NinjaAPI(version="v1", auth=[JWTAuth(),ApiAuthToken()])
# api = NinjaAPI(version="v1")  # just for development purpose we have removed authorization of UniqueId and JWT token

api.add_router("/tasks/", tasks_router)
api.add_router("/accounts/", account_router)
api.add_router("/sprints/", sprint_router)
api.add_router("/epics/", epic_router)


# Custom error handler


@api.exception_handler(ObjectDoesNotExist)
def on_object_does_not_exist(request, exc):
    return api.create_response(request, {"message": " Object Not Found."}, status=404)


@api.exception_handler(ValidationError)
def validation_error_handler(request, exc):
    # Check if `message_dict` is available in the exception
    error_details = (
        exc.message_dict if hasattr(exc, "message_dict") else {"error": str(exc)}
    )
    return api.create_response(
        request,
        {"message": "Validation error occurred.", "details": error_details},
        status=400,
    )


@api.exception_handler(Http404)
def not_found_handler(request, exc):
    return api.create_response(
        request,
        {
            "message": "The Request resource not found.",
            "details": str(exc) if exc else "No object matches the given query.",
        },
        status=404,
    )


@api.exception_handler(Ratelimited)
def handle_rate_limited(request, exc):
    """
    Custom handler for rate-limited requests in Django Ninja.
    - Overrides default 500 error with a structured 429 response.
    - Helps frontend developers handle rate limits gracefully.
    """
    return api.create_response(
        request,
        {
            "message": "Too many requests. Please try again later.",
            "retry_after": "1 hour",
        },
        status=429,
    )
