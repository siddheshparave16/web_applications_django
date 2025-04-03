from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from accounts.models import TaskManagerUser, Organization  
from django.db.models import Q

class CustomAuthenticationForm(AuthenticationForm):
    organization_id = forms.IntegerField(
        required=True,
        widget=forms.TextInput(attrs={'autofocus': True}),
        label="Organization ID",
        help_text="Enter your organization's unique ID"
    )

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        organization_id = self.cleaned_data.get('organization_id')

        if username and password and organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)

                user = TaskManagerUser.objects.filter(username=username, organization=organization).first()

                if not user:
                    raise ValidationError("Invalid username/organization", code='invalid_login')
            
                self.user_cache = authenticate(
                    username=username, password=password )
                
                if self.user_cache is None:
                    raise ValidationError(
                        "Invalid username/password/organization",
                        code='invalid_login'
                    )
            except Organization.DoesNotExist:
                raise ValidationError(
                    "Invalid organization ID",
                    code='invalid_organization'
                )
        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=True,
        help_text="Select which organization this user belongs to"
    )

    class Meta:
        model = TaskManagerUser
        fields = ("username", "email", "organization", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()  # Ensure all fields are processed

        username = cleaned_data.get('username')
        organization = cleaned_data.get('organization')

        if not username:
            self.add_error('username', "Username is required.")

        if not organization:
            self.add_error('organization', "Organization selection is required.")  # ✅ Fix: Error attached to field

        # Ensure username is unique within the same organization
        if username and organization:
            if TaskManagerUser.objects.filter(username=username, organization=organization).exists():
                self.add_error('username', "This username is already taken in this organization.")

        return cleaned_data  # ✅ This ensures `organization` is processed properly



    def clean_email(self):
        email = self.cleaned_data.get('email')
        organization = self.cleaned_data.get('organization')
        
        if email and organization:
            if TaskManagerUser.objects.filter(
                email__iexact=email,
                organization=organization
            ).exists():
                raise ValidationError(
                    "This email is already registered in this organization.",
                    code='duplicate_email'
                )
        return email
    

    def save(self, commit=True):
        user = super().save(commit=False)
        user.organization = self.cleaned_data['organization']
        if commit:
            user.save()
        return user
    

class TaskManagerUserUpdateForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lock organization field completely
        self.fields['organization'].disabled = True
        self.fields['organization'].help_text = "Organization cannot be changed after creation"

    class Meta:
        model = TaskManagerUser
        fields = ("username", "email", "organization", "is_active", "user_permissions")

    def _validate_unique_field(self, field_name, error_message, error_code):
        """Shared validation for unique fields within organization"""
        value = self.cleaned_data.get(field_name)
        if value:
            if TaskManagerUser.objects.exclude(pk=self.instance.pk).filter(
                **{f"{field_name}__iexact": value},
                organization=self.instance.organization
            ).exists():
                raise ValidationError(error_message, code=error_code)
        return value

    def clean_username(self):
        return self._validate_unique_field(
            field_name='username',
            error_message="This username is already taken in your organization.",
            error_code='duplicate_username'
        )

    def clean_email(self):
        return self._validate_unique_field(
            field_name='email',
            error_message="This email is already registered in your organization.",
            error_code='duplicate_email'
        )
    
    