from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class BuyerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)   # email optional

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class CreatorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')