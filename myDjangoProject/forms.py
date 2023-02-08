from django.forms import ModelForm

from .models import Ident
from django import forms
from django import forms

class IdentForm(ModelForm):
    class Meta:
        model = Ident
        fields = ['Username', 'Password', "Password2"]
        widgets = {
            'Password': forms.PasswordInput(),
            'Password2': forms.PasswordInput(),
        }


from django import forms
