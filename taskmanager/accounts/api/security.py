from typing import Optional
from accounts.models import AuthToken
from ninja.security import HttpBearer
from django.http import HttpRequest, HttpResponseForbidden
import jwt
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from django.contrib.auth import get_user_model
from functools import wraps
import logging

logger = logging.getLogger(__name__)


User = get_user_model()


class ApiAuthToken(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> str | None:

        if AuthToken.objects.filter(token=token).exists():
            request.user = AuthToken.objects.get(token=token).user
            return token
        else:
            return None


class JWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[User]:  # type: ignore
        try:
            # Decode the JWT token
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

            # Get the user information from the token's payload
            user = User.objects.get(id=payload["id"])
            request.user = user
            return user

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            # Handle token errors or invalid user
            return None


def required_permission(permission_name):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # print(f"Checking permission: {permission_name} for user {request.user}")
            if not request.user.has_perm(permission_name):
                # logger.warning(f"Permission denied: {permission_name} for user {request.user}.")
                return HttpResponseForbidden("You dont have the required permission!")
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
