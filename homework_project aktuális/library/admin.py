from django.contrib import admin, messages
from .models import Book, Author, BookAuthor, Borrow
from django_object_actions import DjangoObjectActions
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from rangefilter.filters import DateRangeFilter
from .filters import PublishingYearRangeFilter
from django.utils import timezone
from django.contrib.auth import get_user_model
from .forms import BookAdminForm


User = get_user_model()


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1


@admin.register(Book)
class BookAdmin(DjangoObjectActions, admin.ModelAdmin):
    inlines = [BookAuthorInline]
    list_display = ['id', 'title', 'publishing_year', 'available_copies', 'borrowed_status', 'borrowers_list']
    list_filter = (PublishingYearRangeFilter,)
    ordering = ['title', 'publishing_year']
    form = BookAdminForm
    readonly_fields = ('borrowers_list',)
    fieldsets = (
        ('Book', {
            'fields': ('title', 'publishing_year', 'image')
        }),
        ('Other', {
            'fields': ('isbn', 'number_of_pages', 'available_copies')
        }),
    ('Borrowing Info. For action, choose a user and click the save button.', {
        'fields': ('borrowers_list', 'return_from_user', 'borrow_to_user'),
    }),
    )


    actions_on_top = True
    actions_selection_counter = True
    # actions = ['mark_as_borrowed', 'mark_as_available']


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        borrow_user = form.cleaned_data.get('borrow_to_user')
        return_user = form.cleaned_data.get('return_from_user')

        # Visszavétel
        if return_user:
            borrow = Borrow.objects.filter(book=obj, user=return_user, returned_at__isnull=True).first()
            if borrow:
                borrow.returned_at = timezone.now()
                borrow.save()
                obj.available_copies += 1
                obj.is_borrowed = Borrow.objects.filter(book=obj, returned_at__isnull=True).exists()
                obj.save()
                messages.success(request, f"'{obj.title}' has been returned from {return_user.username}.")
            else:
                messages.warning(request, f"{return_user.username} has not borrowed '{obj.title}'.")

        # Kölcsönzés
        if borrow_user:
            already_borrowed = Borrow.objects.filter(book=obj, user=borrow_user, returned_at__isnull=True).exists()
            if not already_borrowed and obj.available_copies > 0:
                Borrow.objects.create(user=borrow_user, book=obj)
                obj.available_copies -= 1
                obj.is_borrowed = obj.available_copies == 0
                obj.save()
                messages.success(request, f"'{obj.title}' has been borrowed by {borrow_user.username}.")
            elif already_borrowed:
                messages.warning(request, f"{borrow_user.username} already borrowed '{obj.title}'.")
            else:
                messages.warning(request, f"No available copies of '{obj.title}' to borrow.")


    def borrowed_status(self, obj):
        return Borrow.objects.filter(book=obj, returned_at__isnull=True).exists()
    borrowed_status.boolean = True
    borrowed_status.short_description = "Borrowed"


    def borrowers_list(self, obj):
        borrows = Borrow.objects.filter(book=obj, returned_at__isnull=True)
        users = [borrow.user.username for borrow in borrows]
        return ", ".join(users) if users else "No borrowers"
    borrowers_list.short_description = 'Borrowers'


    def return_borrower(self, obj):
        # Return a book from a specific borrower.
        borrows = Borrow.objects.filter(book=obj, returned_at__isnull=True)
        if borrows.exists():
            borrower = borrows.first().user
            return f"Return from: {borrower.username}" if borrower else "No active borrow"
        return "No active borrow"
    return_borrower.short_description = 'Return Borrower'


    def return_books(self, request, queryset):
        for book in queryset:
            borrows = Borrow.objects.filter(book=book, returned_at__isnull=True)
            if borrows.exists():
                for borrow in borrows:
                    borrow.returned_at = timezone.now()
                    borrow.save()
                    book.available_copies += 1
                book.is_borrowed = False if not Borrow.objects.filter(book=book, returned_at__isnull=True).exists() else True
                book.save()
                messages.success(request, f"Books successfully returned for '{book.title}'.")
            else:
                messages.warning(request, f"No active borrow found for '{book.title}'.")

    return_books.short_description = "Return selected books"



    def response_change(self, request, obj):
        if "_save" in request.POST:
            return HttpResponseRedirect(f"/admin/library/book/{obj.id}/change/")
        return super().response_change(request, obj)



@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrowed_at', 'returned_at']
    ordering = ['-borrowed_at']
    actions = ['return_individual_borrow']

    def return_individual_borrow(self, request, queryset):
        for borrow in queryset:
            # Visszavesszük a könyvet az adott kölcsönzőtől
            if borrow.returned_at is None:
                borrow.returned_at = timezone.now()
                borrow.save()

                # Növeljük a könyv elérhető példányainak számát
                book = borrow.book
                book.available_copies += 1
                if not Borrow.objects.filter(book=book, returned_at__isnull=True).exists():
                    book.is_borrowed = False
                book.save()

                messages.success(request, f"Successfully returned '{book.title}' from {borrow.user.username}.")
            else:
                messages.warning(request, f"The book '{borrow.book.title}' has already been returned.")

    return_individual_borrow.short_description = "Return selected books from borrowers"

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date_of_birth', 'nationality']
    list_filter = (
        ('date_of_birth', DateRangeFilter),
    )
    ordering = ['name']
    search_fields = ['name']
    inlines = [BookAuthorInline]
    fieldsets = (
        ('Name', {
            'fields': ('name', 'nationality')
        }),
        ('Birth', {
            'fields': ('date_of_birth', 'place_of_birth')
        }),
        ('Death', {
            'fields': ('date_of_death', 'place_of_death')
        })
    )



