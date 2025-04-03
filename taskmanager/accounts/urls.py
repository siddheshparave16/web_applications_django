from django.urls import path
from django.contrib.auth.views import (LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
                                       PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, 
                                       PasswordResetCompleteView)
from accounts.views import register, CustomLoginView
from django.urls import reverse_lazy

app_name = "accounts"

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(template_name="accounts/login.html"), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('password_change/', 
         PasswordChangeView.as_view( template_name="accounts/password_change.html",
          success_url= reverse_lazy("accounts:password_change_done")), 
         name="password_change"),

    path('password_change_done/', 
         PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"), 
         name="password_change_done"),

    path('password_reset/', 
         PasswordResetView.as_view(template_name="accounts/password_reset_form.html", 
                                   email_template_name='accounts/custom_password_reset_email.html',
                                   success_url= reverse_lazy('accounts:password_reset_done')), 
         name="password_reset"),

    path('password_reset/done/', 
         PasswordResetDoneView.as_view(template_name="accounts/password_reset_form_done.html"), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm_form.html", 
                                          success_url=reverse_lazy('accounts:password_reset_complete')), 
         name="password_reset_confirm"),

    path('reset/done/', 
         PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]

