
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Author
from .forms import BookForm, BookRegisterForm

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
    try:
        book = Book.objects.get(id=book_id)
    except:
        return HttpResponse('No book found', status=404)
    context = {
        'book': book
    }
    return render(request, 'library/book_details.html', context)


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