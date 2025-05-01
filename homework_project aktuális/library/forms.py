from django import forms
from django.db import models
from .models import Book, Author, BookAuthor, Borrow
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class BookForm(forms.Form):
    author = forms.CharField(
        max_length=200,
        required=False,
        label=_("Author:")
    )
    title = forms.CharField(
        max_length=200,
        required=False,
        label=_("Title:")
    )
    publishing_year = models.IntegerField(blank=True, null=True)
    isbn = forms.CharField(max_length=200, required=False)
    number_of_pages = models.CharField(max_length=10)
    available_copies = models.IntegerField(default=0)
    is_borrowed = models.BooleanField(default=False)


class BookRegisterForm(forms.ModelForm):
    authors_input = forms.CharField(
        max_length=500,
        required=False,
        label=_("Author(s) (separate with commas):")
    )

    class Meta:
        model = Book
        fields = ['isbn', 'title', 'publishing_year', 'number_of_pages', 'image', 'available_copies']
        labels = {
            'isbn': _("ISBN:"),
            'title': _("Title:"),
            'publishing_year': _("Publishing Year:"),
            'number_of_pages': _("Number of Pages:"),
            'image': _("Cover Image:"),
            'available_copies': _("Available Copies:"),
        }

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


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        required=True,
        label=_("Username"),
        widget=forms.TextInput(attrs={'placeholder': _("Username")})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    age = forms.IntegerField(
        required=True,
        label=_("Age:"),
        validators=[MinValueValidator(18), MaxValueValidator(100)]
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "first_name", "last_name", "age")
        # widgets = {
        #     'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        #     'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        # }


class BookAdminForm(forms.ModelForm):
    borrow_to_user = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    return_from_user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        label="Return book from",
        help_text="Select a user to return this book from."
    )

    class Meta:
        model = Book
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            active_borrows = Borrow.objects.filter(book=self.instance, returned_at__isnull=True)
            user_ids = active_borrows.values_list('user_id', flat=True)
            self.fields['return_from_user'].queryset = User.objects.filter(id__in=user_ids)
            self.fields['borrow_to_user'].queryset = User.objects.exclude(id__in=user_ids)