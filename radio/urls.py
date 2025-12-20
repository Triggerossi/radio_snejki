from django.contrib import admin
from django.urls import path, include
from radio import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('radio/', views.radio_view, name='radio'),
    path('like/<int:song_id>/', views.like_song, name='like_song'),
    path('next-song/', views.next_song_data, name='next_song_data'),
    path('reset-likes/', views.reset_likes, name='reset_likes')
]
