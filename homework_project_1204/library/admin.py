from django.contrib import admin
from .models import Book, Author, BookAuthor

# class BookInline(admin.StackedInline):
#     model = Book
#     extra = 0


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    inlines = [BookAuthorInline]
    list_display = ['id', 'title', 'publishing_year']
    list_filter = ['publishing_year']
    ordering = ['title', 'publishing_year']
    fieldsets = (
        ('Book', {
            'fields': ('title', 'publishing_year', 'image')
        }),
        ('Other', {
            'fields': ('isbn', 'number_of_pages')
        })
    )

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    list_filter = ['nationality']
    ordering = ['name']
    search_fields = ['name']
    inlines = [BookAuthorInline]
    # inlines = [BookInline]
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

