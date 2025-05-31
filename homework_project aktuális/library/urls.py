from django.urls import path
from .views import index, get_books, get_book_details, get_authors, get_author_details, add_book, update_book, borrow_book, return_book, get_account, register, set_language


urlpatterns = [
    path("", index, name="index"),
    path("books/", get_books, name="book_list"),
    path("books/<int:book_id>/", get_book_details, name="book_details"),
    path("authors/", get_authors, name="author_list"),
    path("authors/<int:author_id>/", get_author_details, name="author_details"),
    path("books/add/", add_book, name="add_book"),
    path("books/<int:book_id>/update/", update_book, name="update_book"),
    path('book/<int:book_id>/borrow/', borrow_book, name='borrow_book'),
    path('book/<int:book_id>/return/', return_book, name='return_book'),
    path('account/<int:user_id>/', get_account, name='account'),
    path('register/', register, name='register'),
    path("set_language/", set_language, name="set_language"),
]