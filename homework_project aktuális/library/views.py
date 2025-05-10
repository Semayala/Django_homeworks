from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Author, Borrow
from .forms import BookForm, BookRegisterForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .decorators import superuser_required, custom_permission_required
from django.contrib import messages
import logging
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils import translation
from django.contrib.auth.forms import UserCreationForm


# Create your views here.


def index(request):
    # translation.activate('hu')
    books = Book.objects.all()
    authors = Author.objects.all()
    context = {
        'books': books,
        'authors': authors
    }
    return render(request, 'library/index.html', context)


def get_books(request):
    books = Book.objects.all()
    form = BookForm(request.GET)

    if request.GET and form.is_valid():
        title = form.cleaned_data.get('title')
        publishing_year = form.cleaned_data.get('publishing_year')
        isbn = form.cleaned_data.get('isbn')
        author = form.cleaned_data.get('author')
        number_of_pages = form.cleaned_data.get('number_of_pages')


        if author:
            books = books.filter(authors__name__icontains=author)
        if title:
            books = books.filter(title__icontains=title)
        if publishing_year:
            books = books.filter(publishing_year=publishing_year)
        if isbn:
            books = books.filter(isbn__icontains=isbn)
        if number_of_pages:
            books = books.filter(number_of_pages__icontains=number_of_pages)

    context = {
        'form': form,
        'books': books
    }
    return render(request, 'library/books.html', context)


def get_book_details(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    borrow_record = None
    has_borrowed = False
    borrow_history = []  # Üres lista alapértelmezettként, ha nincs kölcsönzés

    if request.user.is_authenticated:
        borrow_record = Borrow.objects.filter(user=request.user, book=book, returned_at__isnull=True).first()
        has_borrowed = borrow_record is not None

        # Ha adminisztrátor vagy, akkor mindig az összes kölcsönzési előzményt megjelenítjük
        if request.user.is_superuser:
            borrow_history = Borrow.objects.filter(book=book).order_by('-borrowed_at')

    return render(request, 'library/book_details.html', {
        'book': book,
        'has_borrowed': has_borrowed,
        'borrow_record': borrow_record,
        'borrow_history': borrow_history,  # Biztosítjuk, hogy mindig megjelenjenek a kölcsönzési előzmények
    })

def get_authors(request):
    authors = Author.objects.all()

    context = {
        'authors': authors
    }
    return render(request, 'library/authors.html', context)


def get_author_details(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    books = author.books.all()

    context = {
        'author': author,
        'books': books,
    }

    return render(request, 'library/author_details.html', context)

@custom_permission_required('library.add_book')
def add_book(request):
    print(request.GET)
    print(request.POST)

    if request.POST:
        form = BookRegisterForm(request.POST)
        print('DATA', form.data)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    context = {
        'form': BookRegisterForm()
    }
    return render(request, 'library/book_add.html', context)


def is_superuser(user):
    print(user)
    print(user.is_superuser)
    from django.contrib.auth.models import Permission
    permissions = Permission.objects.filter(user=user)
    print(permissions)
    return user.is_superuser


# @login_required
# @user_passes_test(is_superuser)
# @permission_required('library.view_book')
# @permission_required('library.change_book', raise_exception=True)
# @superuser_required
@custom_permission_required('library.change_book')
def update_book(request, book_id):
    print(request)
    print('GET', request.GET)
    print('POST', request.POST)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return HttpResponse('Book not found', status=404)

    if request.POST:
        form = BookRegisterForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            print('DATA:')
            print(form.data)
            print(form.cleaned_data)
            print('____________')
            form.save()
            return redirect('book_details', book_id=book.id)

    form = BookRegisterForm(instance=book)
    context = {
        'form': form,
        'book': book
    }
    return render(request, 'library/book_update.html', context)


logger = logging.getLogger(__name__)


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if Borrow.objects.filter(user=request.user, book=book, returned_at__isnull=True).exists():
        messages.warning(request, "You've already borrowed this book.")
    elif book.available_copies <= 0:
        messages.warning(request, "This book is currently not available.")
    else:
        Borrow.objects.create(user=request.user, book=book)
        book.available_copies -= 1

        # Mindegy, hogy hány példány maradt, a könyv most kölcsönzött
        book.is_borrowed = True
        book.save()

        messages.success(request, f"You have successfully borrowed '{book.title}'.")

    return redirect('book_details', book_id=book.id)


@login_required
def return_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    borrow_record = Borrow.objects.filter(user=request.user, book=book, returned_at__isnull=True).first()

    if borrow_record:
        borrow_record.returned_at = timezone.now()
        borrow_record.save()

        book.available_copies += 1

        if not Borrow.objects.filter(book=book, returned_at__isnull=True).exists():
            book.is_borrowed = False

        book.save()
        messages.success(request, f"You have successfully returned '{book.title}'.")
    else:
        messages.warning(request, "You have not borrowed this book.")

    return redirect('book_details', book_id=book.id)


@login_required
def get_account(request, user_id):
    if request.user.id != user_id:
        return HttpResponse("Unauthorized", status=403)

    user = request.user
    borrowed_books = Borrow.objects.filter(user=user, returned_at__isnull=True).order_by('-borrowed_at')

    return render(request, 'library/account.html', {
        'user': user,
        'borrowed_books': borrowed_books,
    })


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        if language in dict(settings.LANGUAGES):
            translation.activate(language)
            response = redirect(request.POST.get('next', '/'))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
            return response
    return redirect('/')

