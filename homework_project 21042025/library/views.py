
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Author, Borrow
from .forms import BookForm, BookRegisterForm
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .decorators import superuser_required, custom_permission_required
from django.contrib import messages
from django.db import IntegrityError
import logging



# Create your views here.


def index(request):
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
            number_of_pages = books.filter(number_of_pages__icontains=number_of_pages)

    context = {
        'form': form,
        'books': books
    }
    return render(request, 'library/books.html', context)


def get_book_details(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Alapértelmezett érték, ha nem bejelentkezett user
    has_borrowed = None  # Ha nincs bejelentkezve, nem jelenik meg a "Borrowed by you"

    if request.user.is_authenticated:
        has_borrowed = Borrow.objects.filter(user=request.user, book=book).exists()

    return render(request, 'library/book_details.html', {
        'book': book,
        'has_borrowed': has_borrowed,
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
# @permission_required('shopping.view_products')
# @permission_required('shopping.change_products', raise_exception=True)
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

    if Borrow.objects.filter(user=request.user, book=book).exists():
        messages.warning(request, "You've already borrowed this book.")
    elif book.available_copies <= 0:
        messages.warning(request, "This book is currently not available.")
    else:
        # Könyv kölcsönzése
        Borrow.objects.create(user=request.user, book=book)  # Új kölcsönzési rekord létrehozása
        book.available_copies -= 1  # Csökkentjük az elérhető példányokat

        # Ha nincs több elérhető példány, akkor állítsuk be az is_borrowed mezőt True-ra
        if book.available_copies == 0:
            book.is_borrowed = True  # Könyv kölcsönzés alatt

        book.save()

        messages.success(request, f"You have successfully borrowed '{book.title}'.")

    return redirect('book_details', book_id=book.id)

@login_required
def return_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    borrow_record = Borrow.objects.filter(user=request.user, book=book).first()

    if borrow_record:
        borrow_record.delete()  # Kölcsönzési rekord törlése
        book.available_copies += 1  # Növeljük az elérhető példányokat

        # Ha van elérhető példány, akkor a könyv már nem kölcsönzött
        if book.available_copies > 0:
            book.is_borrowed = False

        book.save()

        messages.success(request, f"You have successfully returned '{book.title}'.")
    else:
        messages.warning(request, "You have not borrowed this book.")

    return redirect('book_details', book_id=book.id)



