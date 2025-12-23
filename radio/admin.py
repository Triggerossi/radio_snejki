from django.contrib import admin
from .models import Song, Like, Author, Genre, Dislike

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

@admin.register(Dislike)
class DislikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'id')
    list_filter = ('user',)
    search_fields = ('user__username', 'song__title')
    actions = ['delete_selected_dislikes']

    def delete_selected_dislikes(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Удалено {count} дизлайков.")
    delete_selected_dislikes.short_description = "Удалить выбранные дизлайки"