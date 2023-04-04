from yandex_music import Client
import json


class YandexMusicApi:
    def __init__(self, token):
        self.client = Client(token)

    def like_song(self, song_name):
        self.client.init()
        id_song = self.client.search(song_name)['best']['result']['id']
        result = self.client.users_likes_tracks_add(id_song)
        if result:
            return ""
        else:
            return "error"

    def sort_playlist(self):
        self.client.init()

        song_list = self.client.users_likes_tracks()
        result = {}

        for i in range(len(song_list)):
            try:
                genre = self.client.albums(song_list[i]['album_id'])[0]['genre']
            except:
                genre = 'Не определен'
            if genre is None:
                genre = 'Не определен'

            if genre not in result:
                result[genre] = [i]
            else:
                result[genre].append(i)

        for i in result:
            genre = i
            genre_songs = result[i]
            self.client.users_playlists_create(genre)
            kind = self.client.users_playlists_list()[0]['kind']
            dif = [{"op": "insert", "at": 0, "tracks": []}]
            for song_index in genre_songs:
                id_song = song_list[song_index]['id']
                album_id = song_list[song_index]['album_id']
                dif[0]['tracks'].append({"id": id_song, "albumId": album_id})

            self.client.users_playlists_change(kind, json.dumps(dif))

    def check_token(self):
        self.client.init()
        self.client.users_likes_tracks()

    def song_validate(self, song_name, band_name):
        self.client.init()
        result = self.client.search(song_name, type_='track')
        if result['tracks'] is None:
            return False
        else:
            song_find = set(result['tracks']['results'][0]['title'].lower().split())
            song = set(song_name.lower().split())
            return bool(song & song_find)
