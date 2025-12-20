<!DOCTYPE html>
<html>
<head>
    <title>Radio</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #1e1e1e;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .player {
            text-align: center;
            background: #2c2c2c;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(0,0,0,0.7);
        }
        .cover {
            width: 250px;
            height: 250px;
            object-fit: cover;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .song-info {
            margin-bottom: 20px;
        }
        .song-info h2 {
            margin: 0;
            font-size: 24px;
        }
        .song-info p {
            margin: 5px 0;
            color: #aaa;
        }
        .controls button {
            background: #ff4b5c;
            border: none;
            color: #fff;
            padding: 10px 20px;
            margin: 5px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: 0.3s;
        }
        .controls button:hover {
            background: #ff6f81;
        }
        audio {
            width: 100%;
            margin-bottom: 20px;
            outline: none;
        }
    </style>
</head>
<body>
    {% if song %}
    <div class="player">
        {% if song.cover %}
            <img src="{{ song.cover.url }}" alt="Cover" class="cover">
        {% endif %}
        <div class="song-info">
            <h2>{{ song.title }}</h2>
            <p>{{ song.author }} — {{ song.genre }}</p>
        </div>

        <audio controls autoplay>
            <source src="{{ song.file.url }}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>

        <div class="controls">
            <!-- Лайк -->
            <form method="post" style="display:inline;">
                {% csrf_token %}
                <button type="submit">❤️ Like</button>
            </form>

            <!-- Следующий трек -->
            <form method="get" style="display:inline;">
                <button type="submit">⏭ Next</button>
            </form>
        </div>
    </div>
    {% else %}
        <p>No songs available.</p>
    {% endif %}
</body>
</html>
