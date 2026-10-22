# My Spotify Export

Небольшой скрипт, который выгружает медиатеку Spotify в CSV: любимые треки, сохранённые альбомы и плейлисты. Просто проще свой, чем чужой сервис.

## Что получается

| Файл | Содержимое |
|---|---|
| `liked_tracks.csv` | любимые треки (3 289) |
| `saved_albums.csv` | сохранённые альбомы (1 635) |
| `playlists.csv` | плейлисты и их содержимое |

## Запуск

1. Создайте приложение на [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) и добавьте Redirect URI `http://127.0.0.1:9090`.
2. Передайте ключи через переменные окружения (в код они не попадают):

```bash
export SPOTIFY_CLIENT_ID=...
export SPOTIFY_CLIENT_SECRET=...
# необязательно, по умолчанию http://127.0.0.1:9090
export SPOTIFY_REDIRECT_URI=http://127.0.0.1:9090
```

3. Установите зависимость и запустите:

```bash
pip install spotipy
python export_spotify.py
```

При первом запуске откроется браузер для авторизации в Spotify. Уже заполненные CSV пропускаются, так что скрипт можно безопасно перезапускать после обрыва связи.

## Права

Скрипт запрашивает только чтение: `user-library-read`, `playlist-read-private`, `playlist-read-collaborative`.
