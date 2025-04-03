from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from accounts.forms import CustomAuthenticationForm, CustomUserCreationForm
import logging


logger = logging.getLogger(__name__)


# Create your views here.

def register(request):
    if request.method == "POST":

        form  = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username} !")
            
            # redirect to login page or any other page you want
            return redirect("accounts:login")
    
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {"form": form})

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"User {form.cleaned_data['username']} successfully logged in.")
        return response
    