from django.http import HttpResponse
from django.shortcuts import render
from .models import Library
from .forms import LibraryForm

# Create your views here.


def index(request):
    books = Library.objects.all()
    context = {
        'books': books,
    }
    return render(request, 'library/index.html', context)


def get_books(request):
    print(request.GET)
    print(request.POST)
    books = Library.objects.all()
    if 'clear' in request.GET:
        form = LibraryForm()
    else:
        form = LibraryForm(request.GET)
        if request.GET and form.is_valid():
            print('CLEANED', form.cleaned_data)
            title = form.cleaned_data.get('title')
            author = form.cleaned_data.get('author')
            books = books.filter(
                title__icontains=title,
                author__icontains=author,
            )

    context = {
        'form': form,
        'books': books
    }
    return render(request, 'library/books.html', context)


def get_book_details(request, book_id):
    try:
        book = Library.objects.get(id=book_id)
    except:
        return HttpResponse('No book found', status=404)
    context = {
        'book': book
    }
    return render(request, 'library/book_details.html', context)
