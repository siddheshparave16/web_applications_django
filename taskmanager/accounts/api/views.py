from ninja import Schema, Router
from accounts import services

router = Router(tags=["accounts"])


class TokenSchema(Schema):
    refresh_token: str


@router.post("/access_token", auth=[lambda x: True])
def referesh_token(request, data: TokenSchema):
    try:
        access_token = services.issue_jwt_token_from_refresh_token(
            request.user, data.refresh_token
        )
        return {"access_token": access_token}
    except Exception:
        return {"error": "Invalid Refresh Token."}
