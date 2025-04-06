from django import forms

class BookForm(forms.Form):
    author = forms.CharField(max_length=200, required=False)
    title = forms.CharField(max_length=200, required=False)
    publishing_year = forms.CharField(max_length=200, required=False)
    isbn = forms.CharField(max_length=200, required=False)