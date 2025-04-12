from django.urls import path
from .views import index, get_books, get_book_details, get_authors, get_author_details, add_book, update_book


urlpatterns = [
    path("", index, name="index"),
    path("books", get_books, name="book_list"),
    path("books/<int:book_id>", get_book_details, name="book_details"),
    path("authors", get_authors, name="author_list"),
    path("authors/<int:author_id>", get_author_details, name="author_details"),
    path("books/add", add_book, name="add_book"),
    path("books/<int:book_id>/update", update_book, name="update_book"),
]