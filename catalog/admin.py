from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language

# Register your models here.

# Register the Admin classes for Book using the decorator


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'language', 'display_genre')
    list_filter = ('author', 'language')
    fieldsets = (
        (None, {
            'fields': ('title', 'author')
        }),
        ('Availability', {
            'fields': ('summary', 'language')
        }),
    )

# Register the Admin classes for BookInstance using the decorator


class BookInstanceAdmin(admin.ModelAdmin):

    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower',)
        }),
    )


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',
                    'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]


class GenreAdmin(admin.ModelAdmin):
    pass


class LanguageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Book, BookAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(Language, LanguageAdmin)
