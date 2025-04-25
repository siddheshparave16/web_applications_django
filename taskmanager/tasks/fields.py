from django import forms
from django.core.validators import EmailValidator


email_validator = EmailValidator(message="one or more email addresses are not valid.")


class EmailsListField(forms.CharField):
    def to_python(self, value):
        "Normalize data to list of strings."
        # return an empty list if no input was given
        if not value:
            return []
        else:
            # separate email values and remove whitespace
            return [email.strip() for email in value.split(",")]

    # validate email
    def validate(self, value):
        # check if consist only valid emails
        super().validate(value)

        for email in value:
            email_validator(email)


class PhoneNumberField(forms.IntegerField):
    def to_python(self, value):
        """
        Normalize the input value
         - Strip whitespace from the input.
         - Return None if value is empty
         - Convert the value to an integer if valid.
        """

        if not value:
            return None

        value = str(value).strip()

        try:
            # if user enter leading zero int will remove it
            return int(value)
        except ValueError:
            raise forms.ValidationError("Phone number should consist only of digits.")

    def validate(self, value):
        """
        validate value is a valid phone number
          - Ensure it is positive (no negative numbers).
          - Ensure that number is 10 digit long
        """

        super().validate(value)  # Perform default validation

        if value < 0:
            raise forms.ValidationError("Phone number cannot be negative.")

        if len(str(value)) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits long.")
