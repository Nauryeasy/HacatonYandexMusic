# import openai
import requests
from bs4 import BeautifulSoup
import lxml


class MusicRecommender:
    # def __init__(self, api_key):
        # self.api_key = api_key
        # self.model = "gpt-3.5-turbo"
        # self.messages = [
        #         {"role": "system", "content": "You are a music recommendation bot"},
        #         {"role": "user", "content": "Give a list of similar songs to the song {song_name} by {band_name}"}
        #     ]

    # def choose_music(self, song_name, band_name):
    #     response = self.correct_response(song_name, band_name)
    #     return response
    #
    # def get_response_chat_gpt(self, song_name, band_name):
    #     openai.api_key = self.api_key
    #     messages = self.messages
    #     messages[1]['content'] = messages[1]['content'].format(song_name=song_name, band_name=band_name)
    #     response = openai.ChatCompletion.create(model=self.model, messages=messages).choices[0].message.content.split('\n')
    #     for i in range(len(response)):
    #         if response[i] == '':
    #             response.pop(i)
    #             i -= 1
    #
    #     return response
    #
    # def correct_response(self, song_name, band_name):
    #     response = self.get_response_chat_gpt(song_name, band_name)[2:]
    #     for i in range(len(response)):
    #         if response[i] == '':
    #             response.pop(i)
    #             i -= 1
    #     song_names = list(map(lambda x: x.split('by')[0][x.split('by')[0].index(' '):].replace('"', '').strip(), response))
    #     band_names = list(map(lambda x: x.split('by')[1][1:], response))
    #     return {
    #         'song_names': song_names,
    #         'band_names': band_names
    #     }

    def find_music(self, song_name, band_name):
        url = 'https://lalapoisk.ru/?artist={band_name}&track={song_name}' \
            .format(song_name="+".join(song_name.split()), band_name="+".join(band_name.split()))

        request = requests.get(url)
        content = request.content

        soup = BeautifulSoup(content, 'lxml')
        res = soup.find_all(class_='bb')[3:]
        if len(res) == 0:
            return {'song_names': [], 'band_names': []}
        songs = []

        for i in range(0, 15, 3):
            songs.append(res[i].text)
        if len(songs) == 0:
            return {'song_names': [], 'band_names': []}

        music = {'song_names': [], 'band_names': []}

        for i in songs:
            band, song = i[2:].split(' - ')
            music['song_names'].append(song)
            music['band_names'].append(band)

        return music


class MusicRecommenderException(MusicRecommender):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.messages = [
            {"role": "system", "content": "You are a chatbot"},
            {"role": "user", "content": "Give a list of similar songs to the song {song_name} by {band_name} excluding the songs of the group Ice Nine Kills"},
        ]


# music = MusicRecommender("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")
# print(music.choose_music('The Devils Own', 'Five Fingers Death Punch'))
#
# music_exception = MusicRecommenderException("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")
# print(music_exception.choose_music('Stabbing in the Dark', 'Ice Nine Kills'))
