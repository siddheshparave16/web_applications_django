from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from accounts.forms import CustomAuthenticationForm, CustomUserCreationForm
import logging
from accounts import services
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)


# Create your views here.


def register(request):
    if request.method == "POST":

        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username} !")

            # redirect to login page or any other page you want
            return redirect("accounts:login")

    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"User {form.cleaned_data['username']} successfully logged in.")
        return response


@login_required
def token_generation_view(request):
    """
    A view that displays the user's API token. If a token does not exist,
    it generates a new one. This view handles only GET requests.
    """
    token = services.generate_token(request.user)
    jwt_token = services.issue_jwt_token(request.user)
    refresh_token = services.issue_jwt_refresh_token(request.user)

    return render(
        request,
        "accounts/token_display.html",
        {"token": token, "jwt_token": jwt_token, "refresh_token": refresh_token},
    )
