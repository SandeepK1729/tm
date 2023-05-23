from django import forms  
from .models import User  
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", 
                'gender', 'dob')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_staff = user.user_type in ["admin", "faculty"]
        print(user.is_staff)

        if commit:
            user.save()
        return user
