from django.contrib import admin
from django.urls import path, include
from radio import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('radio.urls')),
    path('', views.login_view),          # главная страница
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('radio/', views.radio_view, name='radio'),
    path('logout/', views.logout_view, name='logout'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)