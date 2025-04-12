from django import forms
from django.db import models
from .models import Book, Author, BookAuthor


class BookForm(forms.Form):
    author = forms.CharField(max_length=200, required=False)
    title = forms.CharField(max_length=200, required=False)
    publishing_year = forms.CharField(max_length=200, required=False)
    isbn = forms.CharField(max_length=200, required=False)
    number_of_pages = models.CharField(max_length=10)


class BookRegisterForm(forms.ModelForm):
    authors_input = forms.CharField(
        max_length=500,
        required=False,
        label="Authors (separate with commas)"
    )

    class Meta:
        model = Book
        fields = ['isbn', 'title', 'publishing_year', 'number_of_pages', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            current_authors = self.instance.authors.all()
            self.fields['authors_input'].initial = ', '.join(
                [author.name for author in current_authors]
            )

    def save(self, commit=True):
        book = super().save(commit=False)

        if commit:
            book.save()

        authors_input = self.cleaned_data.get('authors_input')

        if authors_input:
            author_names = [name.strip() for name in authors_input.split(',')]
            book.authors.clear()

            for name in author_names:
                author, _ = Author.objects.get_or_create(name=name)
                book.authors.add(author)

        if commit:
            book.save()

        return book