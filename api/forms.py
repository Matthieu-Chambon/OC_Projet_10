from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'age', 'can_be_contacted', 'can_data_be_shared', 'password1', 'password2')
