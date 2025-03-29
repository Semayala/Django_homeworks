from django import forms
from .models import Library


class LibraryForm(forms.Form):
    title = forms.CharField(max_length=200, required=False)
    author = forms.CharField(max_length=20, required=False)


