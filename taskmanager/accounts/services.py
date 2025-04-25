from accounts.models import AuthToken
from accounts.models import AbstractUser
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_token(user: AbstractUser) -> str:
    token, _ = AuthToken.objects.get_or_create(user=user)

    return str(token.token)


def issue_jwt_token(user: AbstractUser) -> str:
    """
    Generate a JWT (JSON Web Token) for the given user.

    This function creates a JWT with a payload containing the user's ID and an
    expiration time set to 1 day from the current time. The token is encoded
    using the HS256 algorithm.

    Parameters:
    user (AbstractUser): The user instance for whom the token is being issued.

    Returns:
    str: A JWT token as a string.
    """
    payload = {
        "id": user.id,
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(days=1),  # token expire in One Day
    }

    token = jwt.encode(payload, key=settings.JWT_SECRET_KEY, algorithm="HS256")

    return token


def issue_jwt_refresh_token(user: AbstractUser):

    refresh_token_payload = {
        "id": user.id,
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(days=30),
    }

    refresh_token = jwt.encode(
        refresh_token_payload, settings.JWT_REFRESH_SECRET_KEY, algorithm="HS256"
    )

    return refresh_token


def issue_jwt_token_from_refresh_token(user: AbstractUser, refresh_token) -> str:

    payload = jwt.decode(
        refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"]
    )

    user = User.objects.get(id=payload["id"])

    access_token_payload = {
        "id": user.id,
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }

    return jwt.encode(access_token_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
