import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Song, Like, Author, Genre


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('radio')
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password']
        )
        return redirect('login')
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def radio_view(request):
    # Инициализация списков истории в сессии
    if 'recently_played' not in request.session:
        request.session['recently_played'] = []  # последние 5 сыгранных треков
    if 'recently_liked' not in request.session:
        request.session['recently_liked'] = []   # последние 5 лайкнутых треков

    # Любимые жанры и исполнители
    liked_genres = set(Like.objects.filter(user=request.user)
                       .values_list('song__genre__name', flat=True).distinct())
    liked_authors = set(Like.objects.filter(user=request.user)
                        .values_list('song__author__name', flat=True).distinct())

    # Базовый queryset
    queryset = Song.objects.all()

    # Логика рекомендаций
    if liked_genres or liked_authors:
        session_counter = request.session.get('track_counter', 0)
        request.session['track_counter'] = session_counter + 1
        request.session.modified = True

        # Каждый 4-й трек — НЕ из любимых жанров/исполнителей
        if session_counter % 4 == 0 and session_counter != 0:
            queryset = queryset.exclude(genre__name__in=liked_genres).exclude(author__name__in=liked_authors)
        else:
            queryset = queryset.filter(genre__name__in=liked_genres) | queryset.filter(author__name__in=liked_authors)

        if not queryset.exists():
            queryset = Song.objects.all()

    # Выбор песни
    song = queryset.order_by('?').first()

    if song:
        # Добавляем в историю сыгранных
        recently_played = request.session['recently_played']
        recently_played.append(song.id)
        request.session['recently_played'] = recently_played[-5:]  # храним только 5
        request.session.modified = True

    # Обработка лайка на стартовой загрузке (если POST)
    if request.method == 'POST' and song:
        if not Like.objects.filter(user=request.user, song=song).exists():
            Like.objects.create(user=request.user, song=song)

    context = {
        'song': song,
        'csrf_token': request.COOKIES.get('csrftoken', ''),
        'song_is_liked': Like.objects.filter(user=request.user, song=song).exists() if song else False,
    }

    return render(request, 'radio.html', context)


@require_POST
@login_required
def like_song(request, song_id):
    song = Song.objects.get(id=song_id)
    like, created = Like.objects.get_or_create(user=request.user, song=song)

    if created:
        # Добавляем в список недавно лайкнутых (чтобы не повторялся скоро)
        recently_liked = request.session.get('recently_liked', [])
        recently_liked.append(song.id)
        request.session['recently_liked'] = recently_liked[-5:]
        request.session.modified = True

    return JsonResponse({'status': 'ok'})


@login_required
def next_song_data(request):
    current_id = request.GET.get('current_id')
    current_id = int(current_id) if current_id else None

    # Запрещённые треки: последние 5 сыгранных + последние 5 лайкнутых + текущий
    recently_played = request.session.get('recently_played', [])
    recently_liked = request.session.get('recently_liked', [])
    exclude_ids = set(recently_played + recently_liked)
    if current_id:
        exclude_ids.add(current_id)

    # Любимые жанры и исполнители
    liked_genres = set(Like.objects.filter(user=request.user)
                       .values_list('song__genre__name', flat=True).distinct())
    liked_authors = set(Like.objects.filter(user=request.user)
                        .values_list('song__author__name', flat=True).distinct())

    # Счётчик треков
    session_counter = request.session.get('track_counter', 0)
    request.session['track_counter'] = session_counter + 1
    request.session.modified = True

    # Базовый queryset с исключениями
    queryset = Song.objects.exclude(id__in=exclude_ids)

    # Применяем рекомендации
    if liked_genres or liked_authors:
        if session_counter % 4 == 0 and session_counter != 0:
            # Каждый 4-й — другой стиль
            preferred = queryset.exclude(genre__name__in=liked_genres).exclude(author__name__in=liked_authors)
        else:
            preferred = queryset.filter(genre__name__in=liked_genres) | queryset.filter(author__name__in=liked_authors)

        if preferred.exists():
            queryset = preferred

    # Fallback, если ничего не осталось
    if not queryset.exists():
        queryset = Song.objects.all()
        if current_id:
            queryset = queryset.exclude(id=current_id)

    # Выбор песни
    song = random.choice(list(queryset.order_by('?')))

    # Обновляем историю сыгранных
    recently_played = request.session.get('recently_played', [])
    recently_played.append(song.id)
    request.session['recently_played'] = recently_played[-5:]
    request.session.modified = True

    # Ответ
    is_liked = Like.objects.filter(user=request.user, song=song).exists()
    likes_count = Like.objects.filter(song=song).count()

    return JsonResponse({
        'id': song.id,
        'title': song.title,
        'author': song.author.name,
        'genre': song.genre.name,
        'file_url': song.file.url,
        'cover_url': song.cover.url if song.cover else '',
        'is_liked': is_liked,
        'likes_count': likes_count,
    })


@login_required
def reset_likes(request):
    if request.method == 'POST':
        # Удаляем все лайки пользователя
        Like.objects.filter(user=request.user).delete()

        # Полная очистка сессии
        keys_to_clear = ['track_counter', 'recently_played', 'recently_liked']
        for key in keys_to_clear:
            if key in request.session:
                del request.session[key]
        request.session.modified = True

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'error'}, status=400)