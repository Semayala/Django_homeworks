from django.contrib import admin
from .models import Library
# Register your models here.


class LibraryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publishing_year']
    list_filter = ['publishing_year', 'author']
    ordering = ['title', 'publishing_year']
    fieldsets = (
        ('Book', {
            'fields': ('title', 'author','publishing_year')
        }),
        ('Other', {
            'fields': ('isbn', 'number_of_pages')
        })
    )



admin.site.register(Library, LibraryAdmin)