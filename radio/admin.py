from django.contrib import admin
from .models import Song, Like, Author, Genre

# Простая регистрация без лишних полей
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre')
    search_fields = ('title', 'author__name', 'genre__name')
    list_filter = ('genre', 'author')

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'id')
    list_filter = ('user',)
    search_fields = ('user__username', 'song__title')