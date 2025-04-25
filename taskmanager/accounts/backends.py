from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend
import logging


logger = logging.getLogger(__name__)


class OrganizationUsernameOrEmailBackend(ModelBackend):
    def authenticate(
        self, request, username=None, password=None, organization_id=None, **kwargs
    ):
        UserModel = get_user_model()

        # Log the inputs for debugging
        logger.debug(
            f"Authenticating user: {username}, Organization ID: {organization_id}"
        )

        if organization_id is None:
            logger.warning("Organization ID is missing!")
            return None

        try:
            user = UserModel.objects.filter(
                (Q(username__iexact=username) | Q(email__iexact=username))
                & Q(organization_id=organization_id)
            ).first()

            # Log if no user is found
            if not user:
                logger.warning(
                    f"No user found with username/email: {username} and organization_id: {organization_id}"
                )
                return None

            # If user is found, verify password
            if user.check_password(password):
                logger.info(f"User {username} authenticated successfully.")
                return user
            else:
                logger.warning(f"Incorrect password for user: {username}")
                return None

        except UserModel.DoesNotExist:
            return None  # Return None if no matching user is found

    def get_user(self, user_id):
        UserModel = get_user_model()

        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
