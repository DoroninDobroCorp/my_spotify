import os
import time
import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from requests.exceptions import RequestException

CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:9090')

SCOPE = 'user-library-read playlist-read-private playlist-read-collaborative'

def safe_api_call(func, *args, **kwargs):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Если статус-код 403 (Forbidden) или 404 (Not Found), сразу выбрасываем исключение
            if hasattr(e, 'http_status') and e.http_status in (403, 404):
                raise e
            if attempt == max_retries - 1:
                raise e
            print(f"\n[Внимание] Сетевой сбой Spotify API ({e}). Повтор {attempt + 1}/{max_retries} через 3 сек...")
            time.sleep(3)


def main():
    print("Авторизация в Spotify...")
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            open_browser=True
        ),
        requests_timeout=30
    )

    user = sp.current_user()
    print(f"Успешно авторизован как: {user['display_name']} ({user['id']})\n")

    # 1. Экспорт Любимых треков (Liked Songs)
    if os.path.exists('liked_tracks.csv') and os.path.getsize('liked_tracks.csv') > 1000:
        print("[1/3] liked_tracks.csv уже существует и содержит данные, пропуск.")
    else:
        export_liked_tracks(sp)

    # 2. Экспорт Сохраненных альбомов (Saved Albums)
    if os.path.exists('saved_albums.csv') and os.path.getsize('saved_albums.csv') > 1000:
        print("[2/3] saved_albums.csv уже существует и содержит данные, пропуск.")
    else:
        export_saved_albums(sp)

    # 3. Экспорт Плейлистов (Playlists)
    export_playlists(sp)

    print("\nГотово! Все CSV файлы успешно созданы.")

def export_liked_tracks(sp):
    print("[1/3] Экспорт любимых треков...")
    with open('liked_tracks.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Track Name', 'Artist(s)', 'Album', 'Duration (ms)', 'Release Date', 'Spotify URL'])

        results = safe_api_call(sp.current_user_saved_tracks, limit=50)
        total = results['total'] if results else 0
        count = 0

        while results:
            for item in results['items']:
                track = item['track']
                name = track['name']
                artists = ", ".join([a['name'] for a in track['artists']])
                album = track['album']['name']
                duration = track['duration_ms']
                release_date = track['album']['release_date']
                url = track['external_urls'].get('spotify', '')

                writer.writerow([name, artists, album, duration, release_date, url])
                count += 1

            print(f"Обработано треков: {count}/{total}", end='\r')
            if results.get('next'):
                results = safe_api_call(sp.next, results)
            else:
                break
    print(f"\nСохранено в liked_tracks.csv ({count} треков)")

def export_saved_albums(sp):
    print("\n[2/3] Экспорт сохраненных альбомов...")
    with open('saved_albums.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Album Name', 'Artist(s)', 'Total Tracks', 'Release Date', 'Spotify URL'])

        results = safe_api_call(sp.current_user_saved_albums, limit=50)
        total = results['total'] if results else 0
        count = 0

        while results:
            for item in results['items']:
                album = item['album']
                name = album['name']
                artists = ", ".join([a['name'] for a in album['artists']])
                total_tracks = album['total_tracks']
                release_date = album['release_date']
                url = album['external_urls'].get('spotify', '')

                writer.writerow([name, artists, total_tracks, release_date, url])
                count += 1

            print(f"Обработано альбомов: {count}/{total}", end='\r')
            if results.get('next'):
                results = safe_api_call(sp.next, results)
            else:
                break
    print(f"\nСохранено в saved_albums.csv ({count} альбомов)")

def export_playlists(sp):
    print("\n[3/3] Экспорт плейлистов и их содержимого...")
    with open('playlists.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Playlist Name', 'Track Name', 'Artist(s)', 'Album', 'Added At', 'Spotify URL'])

        playlists = safe_api_call(sp.current_user_playlists)
        playlist_count = 0

        while playlists:
            for pl in playlists['items']:
                pl_name = pl['name']
                playlist_count += 1
                print(f"Обработка плейлиста '{pl_name}'...")

                try:
                    tracks_data = safe_api_call(sp.playlist_tracks, pl['id'])
                    while tracks_data:
                        for item in tracks_data['items']:
                            track = item.get('track')
                            if not track:
                                continue
                            
                            name = track.get('name', '')
                            artists = ", ".join([a['name'] for a in track.get('artists', [])])
                            album = track.get('album', {}).get('name', '')
                            added_at = item.get('added_at', '')
                            url = track.get('external_urls', {}).get('spotify', '')

                            writer.writerow([pl_name, name, artists, album, added_at, url])

                        if tracks_data.get('next'):
                            tracks_data = safe_api_call(sp.next, tracks_data)
                        else:
                            break
                except Exception as err:
                    print(f"[Пропущен плейлист '{pl_name}']: {err}")

            if playlists.get('next'):
                playlists = safe_api_call(sp.next, playlists)
            else:
                break

    print(f"\nСохранено в playlists.csv (всего плейлистов: {playlist_count})")

if __name__ == '__main__':
    main()
