from django.contrib import admin, messages
from .models import Book, Author, BookAuthor, Borrow
from django_object_actions import DjangoObjectActions
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from rangefilter.filters import DateRangeFilter
from .filters import PublishingYearRangeFilter


User = get_user_model()

# class BookInline(admin.StackedInline):
#     model = Book
#     extra = 0


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1


@admin.register(Book)
class BookAdmin(DjangoObjectActions, admin.ModelAdmin):
    inlines = [BookAuthorInline]
    list_display = ['id', 'title', 'publishing_year', 'available_copies', 'is_borrowed']
    list_filter = (PublishingYearRangeFilter,)
    ordering = ['title', 'publishing_year']
    fieldsets = (
        ('Book', {
            'fields': ('title', 'publishing_year', 'image')
        }),
        ('Other', {
            'fields': ('isbn', 'number_of_pages', 'available_copies', 'is_borrowed')
        })
    )

    actions_on_top = True
    actions_selection_counter = True
    actions = ['mark_as_borrowed', 'mark_as_available']
    change_actions = ['borrow_book', 'return_book']

    def get_queryset(self, request):
        """
        Frissítjük a könyvek `is_borrowed` mezőjét, hogy csak azok legyenek "kölcsönzöttként"
        tüntetve, amik val=ban ki vannak kölcsönözve
        """
        queryset = super().get_queryset(request)

        # A könyvek frissítése, hogy tükrözzék a helyes kölcsönzési státust
        for book in queryset:
            # Ha van bármilyen kölcsönzés, akkor a könyvet kölcsönzöttként kezeljük
            if Borrow.objects.filter(book=book).exists():
                book.is_borrowed = True
            else:
                book.is_borrowed = False
            book.save()

        return queryset

    def user_has_borrowed(self, obj):
        """
        Display a checkmark if the user has borrowed the book.
        """
        if Borrow.objects.filter(user=self.request.user, book=obj).exists():
            return "✔️"
        else:
            return "❌"

    user_has_borrowed.short_description = 'Borrowed by You'

    def mark_as_borrowed(self, request, queryset):
        for book in queryset:
            already_borrowed = Borrow.objects.filter(book=book, user=request.user).exists()
            if already_borrowed:
                messages.warning(request, f"You already borrowed '{book.title}'.")
            else:
                Borrow.objects.create(user=request.user, book=book)
                book.available_copies -= 1  # Csökkentjük az elérhető példányokat
                book.is_borrowed = True  # Frissítjük az is_borrowed mezőt
                book.save()
                messages.success(request, f"Successfully borrowed '{book.title}' for {request.user}.")

    def mark_as_available(self, request, queryset):
        for book in queryset:
            borrow = Borrow.objects.filter(book=book, user=request.user).first()
            if borrow:
                borrow.delete()
                book.available_copies += 1  # Növeljük az elérhető példányok számát
                book.is_borrowed = False  # Frissítjük az is_borrowed mezőt
                book.save()
                messages.success(request, f"'{book.title}' successfully returned.")
            else:
                messages.warning(request, f"No borrow record found for '{book.title}' by {request.user}.")

    def borrow_book(self, request, queryset):
        if not hasattr(queryset, '__iter__'):  # Ha csak egy könyv van kiválasztva
            queryset = [queryset]

        for book in queryset:
            # Ellenőrizzük, hogy a felhasználó már kölcsönözte-e
            if Borrow.objects.filter(user=request.user, book=book).exists():
                messages.warning(request, f"Already borrowed '{book.title}'.")
            elif book.available_copies > 0:  # Csak akkor kölcsönözhető, ha van elérhető példány
                try:
                    Borrow.objects.create(user=request.user, book=book)
                    book.available_copies -= 1  # Csökkentjük az elérhető példányokat
                    book.is_borrowed = True  # Frissítjük az is_borrowed mezőt
                    book.save()
                    messages.success(request, f"Successfully borrowed '{book.title}'.")
                except IntegrityError:
                    messages.warning(request, f"Already borrowed '{book.title}'.")
            else:
                messages.warning(request, f"'{book.title}' is not available.")

    def return_book(self, request, obj):
        borrow = Borrow.objects.filter(user=request.user, book=obj).first()
        if borrow:
            borrow.delete()
            obj.available_copies += 1  # Növeljük az elérhető példányok számát
            obj.is_borrowed = False  # Frissítjük az is_borrowed mezőt
            obj.save()
            messages.success(request, f"You returned '{obj.title}'.")
        else:
            messages.warning(request, f"You haven't borrowed '{obj.title}'.")

    def response_change(self, request, obj):
        if "_save" in request.POST:
            return HttpResponseRedirect(f"/admin/library/book/{obj.id}/change/")
        return super().response_change(request, obj)


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrowed_at']
    ordering = ['-borrowed_at']


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

# admin.site.register(Book, BookAdmin, BookInline)
# admin.site.register(Author, AuthorAdmin)

