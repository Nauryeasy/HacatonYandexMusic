from flask import Flask, request
from Dialog import Dialog
from Handler import Handler
from Response import Responser
from StartDialog import StartDialog
from TimeoutDialog import TimeoutDialog
from MiddlewareDialog import MiddleWareDialog
from globalStorage import *
import openai
from threading import Thread
import traceback
import random
from YandexMusicApi import YandexMusicApi
from MusicRecomender import MusicRecommender, MusicRecommenderException
import requests
from bs4 import BeautifulSoup
import lxml


# def get_info(url: str) -> list:
#     headers = {
#         'authority': 'downloader.freemake.com',
#         'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Yandex";v="22"',
#         'dnt': '1',
#         'x-cf-country': 'RU',
#         'sec-ch-ua-mobile': '?0',
#         'x-user-platform': 'Win32',
#         'accept': 'application/json, text/javascript, */*; q=0.01',
#         'x-user-browser': 'YaBrowser',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                       'Chrome/98.0.4758.141 YaBrowser/22.3.3.852 Yowser/2.5 Safari/537.36',
#         'x-analytics-header': 'UA-18256617-1',
#         'x-request-attempt': '1',
#         'x-user-id': '94119398-e27a-3e13-be17-bbe7fbc25874',
#         'sec-ch-ua-platform': '"Windows"',
#         'origin': 'https://www.freemake.com',
#         'sec-fetch-site': 'same-site',
#         'sec-fetch-mode': 'cors',
#         'sec-fetch-dest': 'empty',
#         'referer': 'https://www.freemake.com/ru/free_video_downloader/',
#         'accept-language': 'ru,en;q=0.9,uk;q=0.8',
#     }
#
#     # поиск названия песни
#     r = str(requests.get(url).text)
#     first_index = r.find('<title>')
#     second_index = r.find('- YouTube', first_index+7)
#     filename = r[first_index+7 : second_index]
#     print(filename)
#
#     # получение ссылки на сайт с всей инфой о видео
#     if 'v=' in url:
#         video_id = url.split('v=')[1].split('&')[0]
#     else:
#         video_id = url.split('/')[-1]
#     print(video_id)
#     info_json_url = f'https://downloader.freemake.com/api/videoinfo/{video_id}'
#
#     # получение json со всеми ссылками на это видео
#     video_links_json = requests.get(url=info_json_url, headers=headers).json()
#     # отбор худшего видео
#     url = video_links_json['qualities'][-1]['url']
#     print(url)
#
#     # запись байтов видео
#     bytes_of_video = b''
#     r = requests.get(url, stream=True)
#     for chunk in r.iter_content(chunk_size=1024):
#         bytes_of_video += chunk
#         print('Download...')
#
#     return [bytes_of_video, filename]


# def send_to_yandex(filename: str, bytes_of_video: bytes, post_target: str) -> bool:
#     files = {'file': (filename, bytes_of_video, 'audio/mpeg')}
#
#     headers = {
#         'Accept': '*/*',
#         'Accept-Language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7',
#         'Connection': 'keep-alive',
#     }
#
#     # отправка на post-target
#     resp = requests.post(post_target, files=files, headers=headers)
#     return str(resp.content)


def find_music_def(event):
    if 'song_name' not in event['state']['session']:
        text = ['Назовите мне песню, а я подберу вам похожие', 'Предложите мне название песни, а я найду вам похожие',
                'К какой песне вы бы хотели подобрать похожие?', 'Назовите песню, чтобы я сделала подборку похожих']
        message = random.choice(text)
        return {
            "text": message,
            "tts": message,
            "buttons": [],
            "session_state": {
                "branch": "find_music",
                "song_name": "",
                "find_music": ""
            }
        }
    else:
        if 'access_token' in event['state']['user']:
            yandex_music_api = YandexMusicApi(event['state']['user']['access_token'])
        return {
            "text": "Напишите название группы или исполнителя",
            "tts": "Напишите название группы",
            "buttons": [],
            "session_state": {
                "branch": "find_music",
                "find_music_completed": "",
                "song_name": event["request"]["original_utterance"]
            }
        }


def find_music_completed_def(event):
    try:
        yandex_music_api = YandexMusicApi('y0_AgAAAAA_-b6BAAG8XgAAAADb-NOHjdJntsKzQZqp4IichAedE4Mnfok')
        result = yandex_music_api.song_validate(event['state']['session']['song_name'], event["request"]["original_utterance"])

        if result:
            text = ['Вот список похожих песен:\n', 'Вот подборка похожих песен:\n']
            music = music_recomender.find_music(event['state']['session']['song_name'], event["request"]["original_utterance"])
            message = random.choice(text)
            for i in range(len(music['song_names'])):
                message += f'{i + 1}. "{music["song_names"][i]}" by {music["band_names"][i]} \n'

            message += "Если хотите поставить лайк на песню - напишите ее номер"

            if len(music["song_names"]) != 0:
                return {
                        "text": message,
                        "tts": message,
                        "buttons": [
                            "Главное меню"
                        ],
                        "session_state": {
                            "branch": "find_music_completed",
                            "music_list": music,
                        }
                    }
            else:
                return {
                        "text": 'Песни по вашему запросу не найдены :(\n'
                                'Попросите меня подобрать похожие песни и мы попробуем снова',
                        "tts": 'Песни по вашему запросу не найдены'
                               'Попросите меня подобрать похожие песни и мы попробуем снова',
                        "buttons": [
                            "Главное меню"
                        ],
                        "session_state": {
                            "branch": "main_menu",
                            "music_list": music,
                        }
                    }
        else:
            return {
                "text": 'Нам кажется, что вы ввели несуществующую песню или допустили ошибку, чтобы попробовать еще раз скажите: подбери мне похожие песни',
                "tts": 'Нам кажется, что вы ввели несуществующую песню или допустили ошибку, чтобы попробовать еще раз скажите: подбери мне похожие песни',
                "buttons": [
                    "Главное меню"
                ],
                "session_state": {
                    "branch": "main_menu",
                }
            }
    except Exception:
        print(traceback.format_exc())
        return {
            "text": "Извините, произошла непредвиденная ошибка, попробуйте позже \n"
                    "Так же хотим напомнить, что данная функция пока что не работает с русскими песнями",
            "tts": "Извините, произошла непредвиденная ошибка, попробуйте позже."
                    "Так же хотим напомнить, что данная функция пока что не работает с русскими песнями",
            "buttons": [
                "Главное меню"
            ],
            "session_state": {
                "branch": "main_menu",
            }
        }


def authorization_def(event):
    return {
            "text":
                """
Для использование некоторых функций навыка требуется авторизация
Для авторизации скачайте расширение для вашего браузера (Ссылки находятся ниже в кнопках)
После чего авторизируйтесь и нажмите кнопку "скопировать токен"
Далее напишите "Ввести токен" в навыке и отправьте скопированный токен.
Для авторизации используется стороннее расширение, так как разработчикам не удалось
опубликовать свое, так как сейчас запрещено это делать из России. Но разработчики
Всеми силами ищут способ преодолеть это ограничение. Так же в разработке мобильное приложение для получения данного токена
                """,
            "tts": """
Для использования навыка вам следует пройти авторизацию на устройстве с экраном
Для использование некоторых функций навыка требуется авторизация
Для авторизации скачайте расширение для вашего браузера (Ссылки находятся ниже в кнопках)
После чего авторизируйтесь и нажмите кнопку "скопировать токен"
Далее скажите "Ввести токен" в навыке и отправьте скопированный токен.
Для авторизации используется стороннее расширение, так как разработчикам не удалось
опубликовать свое, так как сейчас запрещено это делать из России. Но разработчики
Всеми силами ищут способ преодолеть это ограничение. Так же в разработке мобильное приложение для получения данного токена
""",
            "buttons": [
                {
                    'title': 'Расширение для Google Chrome',
                    'url': 'https://chrome.google.com/webstore/detail/yandex-music-token/lcbjeookjibfhjjopieifgjnhlegmkib',
                    'hide': False
                },
                {
                    'title': 'Расширение для Mozilla FireFox',
                    'url': 'https://addons.mozilla.org/en-US/firefox/addon/yandex-music-token/',
                    'hide': False
                },
                "Ввести токен"
            ],
            "session_state": {
                "branch": "authorization"
            },
            "user_state_update": {
                "access_token": None
            },
    }


def get_access_token_def(event):
    if "access_token" in event['state']['user']:
        try:
            yandex_music_api = YandexMusicApi(event["request"]["original_utterance"])
            yandex_music_api.check_token()
            return {
                "text": "Вы успешно прошли прошли авторизацию!",
                "tts": "Вы успешно прошли прошли авторизацию!",
                "buttons": [
                    "Главное меню"
                ],
                "session_state": {
                    "branch": "get_access_token"
                },
                "user_state_update": {
                    "access_token": event["request"]["original_utterance"]
                },
            }
        except:
            return {
                "text": "Ваш токен оказался невалидным, попробуйте еще раз.\nВведите ваш токен:",
                "tts": "Ваш токен оказался невалидным, попробуйте еще раз. Введите ваш токен",
                "buttons": [
                    "Главное меню"
                ],
                "session_state": {
                    "branch": "get_access_token",
                    "get_access_token": ""
                },
                "user_state_update": {
                    "access_token": "<token>"
                },
            }
    else:
        return {
            "text": "Введите ваш токен:",
            "tts": "Введите ваш токен",
            "buttons": [
                "Главное меню"
            ],
            "session_state": {
                "branch": "get_access_token",
                "get_access_token": ""
            },
            "user_state_update": {
                "access_token": "<token>"
            },
        }


def main_menu_def(event):
    return {
        "card": {
            "type": "BigImage",
            "image_id": "997614/bfada651fa355c92fe73",
            "title": "ГЛАВНОЕ МЕНЮ",
            "description":
                """
                Добро пожаловать в навык "Менеджер музыки"! Для того, чтобы узнать функционал навыка скажите: 'Что ты умеешь?'\n
    Чтобы узнать как пользоваться навыком обратитесь в помощь, для этого скажите: 'Помощь'. \n
Для многих функций навыка требуется авторизация. Для того, чтобы авторизироваться скажите: 'Авторизация'.""",
        },
        "text": "text",
        "tts":
            """
        Добро пожаловать в навык "Менеджер музыки"! Для того, чтобы узнать функционал навыка скажите: 'Что ты умеешь?'\n
Чтобы узнать как пользоваться навыком обратитесь в помощь, для этого скажите: Помощь. \n
Для многих функций навыка требуется авторизация. Для того, чтобы авторизироваться скажите: Авторизация.""",
        "buttons": [
            "Подбери песни",
            "Отсортируй плейлист",
            "Добавь с YouTube",
            "Авторизация",
            "Помощь",
            "Что ты умеешь",
            "Выход"
        ],
        "session_state": {
            "branch": "main_menu"
        }
    }


def back_def(event):
    try:
        return dialog_handler.dialogs_dict[dialog_handler.get_state(event)].last_state.get_response_info(event)
    except:
        return main_menu.get_response_info(event)


def help_menu_def(event):
    return {
        "text": """
Я могу сделать подборку похожих песен, по предложенной вами и добавить их в раздел "Моя Музыка" приложения яндекс музыка. Для этого скажите: Подбери песни. \n
Кроме того, в мои умения входит сортировка вашей любимой музыки по жанрам, для этого скажите: Отсортируй плейлист. А так же возможен перенос музыки из YouTube в Яндекс Музыку, но данная функция недоступна до переезда навыка с Yandex Cloud на собственный хостинг.\n
Также вы можете задать вопрос разработчикам навыка или узнать, как связаться с ними.
                """,
        "tts": """Я могу сделать подборку похожих песен, по предложенной вами и добавить их в раздел "Моя Музыка" приложения яндекс музыка. Для этого скажите: Подбери песни. \n
Кроме того, в мои умения входит сортировка вашей любимой музыки по жанрам, для этого скажите: Отсортируй плейлист. А так же возможен перенос музыки из YouTube в Яндекс Музыку, но данная функция недоступна до переезда навыка с Yandex Cloud на собственный хостинг.
Также вы можете задать вопрос разработчикам навыка или узнать, как связаться с ними, сказав 'Я хочу задать вопрос или контакты разработчиков соответственно'.""",
        "buttons": [
            "Как связаться с разработчиками?",
            "Задать вопрос",
            "Что ты умеешь",
            "Назад"
        ],
        "session_state": {
            "branch": "help_menu"
        }
    }


def connect_with_developers_def(event):
    text = ['Вот контакты разработчиков:\n', 'Контакты для связи с разработчиками:\n',
            'Чтобы связаться с разработчиками воспользуйтесь контактами:\n'
            ]
    message = random.choice(text)
    contacts = "Email: koertyf@gmail.com\n" \
               "Telegram: @Nauryeasy"
    return {
        "text": message + contacts,
        "tts": message + contacts,
        "buttons": [
            "Главное меню",
            "Назад"
        ],
        "session_state": {
            "branch": "connect_developers"
        }
    }


def sort_playlist_def(event):
    if 'access_token' in event['state']['user']:
        yandex_music_api = YandexMusicApi(event['state']['user']['access_token'])
        th = Thread(target=yandex_music_api.sort_playlist)
        th.start()
        return {
            "text": "Сортировка была успешно запущена. Загляните в свои плейлисты через некоторое время, чтобы увидеть результат",
            "tts": "Сортировка была успешно запущена. Загляните в свои плейлисты через некоторое время, чтобы увидеть результат",
            "buttons": [
                "Главное меню",
            ],
            "session_state": {
                "branch": "main_menu"
            }
        }
    else:
        return {
            "text": "Вы не авторизированы, для того, чтобы отсортировать плейлист перейдите в главное меню и авторизируйтесь",
            "tts": "Вы не авторизированы, для того, чтобы отсортировать плейлист перейдите в главное меню и авторизируйтесь",
            "buttons": [
                "Главное меню",
            ],
            "session_state": {
                "branch": "main_menu",
            }
        }


def add_song_def(event):
    if 'access_token' in event['state']['user']:
        tokens = event['request']['nlu']['tokens']
        for i in tokens:
            try:
                song_index = int(i)
                break
            except:
                pass

        try:
            song = event['state']['session']['music_list']['song_names'][song_index - 1] + ' ' + event['state']['session']['music_list']['band_names'][song_index - 1]
        except:
            return {
                "text": "Индекс песни не был найден в вашем запросе, попробуйте еще раз",
                "tts": "Индекс песни не был найден в вашем запросе, попробуйте еще раз",
                "buttons": [
                    "Главное меню",
                ],
                "session_state": {
                    "branch": "add_song",
                    "music_list": event['state']['session']["music_list"]
                }
            }

        try:
            yandex_music_api = YandexMusicApi(event['state']['user']['access_token'])
            result = yandex_music_api.like_song(song)
            if result == "error":
                return {
                    "text": "Песня по какой-то причине не была лайкнута, попробуйте еще раз",
                    "tts": "Песня по какой-то причине не была лайкнута, попробуйте еще раз",
                    "buttons": [
                        "Главное меню",
                    ],
                    "session_state": {
                        "branch": "add_song",
                        "music_list": event['state']['session']["music_list"]
                    }
                }
            else:
                text = ['Трек успешно добавлен! Могу добавить что-то еще по вашему желанию.',
                        'Песня была лайкнута, хотите лайкнуть что-то еще или вернемся в главное меню?',
                        'Трек добавлен, можете наслаждаться прослушиванием! Желаете добавить что-то еще или вернемся в главное меню?'
                    ]
                message = random.choice(text)
                return {
                    "text": message,
                    "tts": message,
                    "buttons": [
                        "Главное меню",
                    ],
                    "session_state": {
                        "branch": "add_song",
                        "music_list": event['state']['session']["music_list"]
                    }
                }
        except:
            return {
                    "text": "Песня по какой-то причине не была лайкнута, попробуйте еще раз",
                    "tts": "Песня по какой-то причине не была лайкнута, попробуйте еще раз",
                    "buttons": [
                        "Главное меню",
                    ],
                    "session_state": {
                        "branch": "add_song",
                        "music_list": event['state']['session']["music_list"]
                    }
                }

    else:
        return {
            "text": "Вы не авторизированы, для того, чтобы лайкать песни перейдите в главное меню и авторизируйтесь",
            "tts": "Вы не авторизированы, для того, чтобы лайкать песни перейдите в главное меню и авторизируйтесь",
            "buttons": [
                "Главное меню",
            ],
            "session_state": {
                "branch": "add_song",
                "music_list": event['state']['session']["music_list"]
            }
        }


def question_developers_def(event):
    if 'question_text' not in event['state']['session']:
        text = ['Напишите ваш вопрос, чтобы я отправила его разработчикам', 'Задайте вопрос, и я отправлю его разработчикам']
        message = random.choice(text)
        return {
            "text": message,
            "tts": message,
            "buttons": [
                "Главное меню",
                "Назад"
            ],
            "session_state": {
                "branch": "question",
                "question": "",
                "question_text": ""
            }
        }
    elif 'email' not in event['state']['session']:
        return {
            "text": "Напишите вашу почту, чтобы получить ответ:",
            "tts": "Напишите вашу почту, чтобы получить ответ:",
            "buttons": [
                "Главное меню",
                "Назад"
            ],
            "session_state": {
                "branch": "question",
                "question": "",
                "email": "",
                "question_text": event["request"]["original_utterance"]
            }
        }
    else:
        print(event['state']['session']['question_text'], event["request"]["original_utterance"])
        text = ['Ваш вопрос успешно отправлен разработчикам!',
                'Вопрос был успешно доставлен!']
        message = random.choice(text)
        return {
            "text": message,
            "tts": message,
            "buttons": [
                "Главное меню",
                "Назад"
            ],
            "session_state": {
                "branch": "help_menu",
            }
        }



def exit_menu_def(event):
    if 'exit_opinion' in event['state']['session']:
        yes_list = ['да', 'конечно', 'угу', 'ага', 'точно', 'именно', "выйди", "выход"]
        no_list = ['нет', 'не', 'ноуп', 'никогда', 'ненадо', 'ненужно']
        if event['request']['command'] in yes_list:
            text = ['Было очень приятно вам помочь! С нетерпением жду, как смогу сделать это снова, Ня!',
                    'Была рада вам помочь! Надеюсь еще увидимся, ня!',
                    'Хорошего дня! Если понадоблюсь, обращайтесь, ня!',
                    'Была рада провести с вами время! Жду, не дождусь, когда смогу помочь вам снова, ня!'
                    ]
            message = random.choice(text)
            return {
                "text": message,
                "tts": message,
                "buttons": [
                ],
                "end_session": True,
                "session_state": {
                    "branch": "exit_menu"
                }
            }
        elif event['request']['command'] in no_list:
            return {
                "text": 'Вот и правильно!',
                "tts": 'Вот и правильно!',
                "buttons": [
                    "Главное меню",
                    "Назад"
                ],
                "session_state": {
                    "branch": "exit_menu"
                }
            }
    else:
        text = ['Вы точно хотите выйти?', 'Вы уверены что хотите выйти?', 'Желаете выйти из навыка?']
        message = random.choice(text)
        return {
            "text": message,
            "tts": message,
            "buttons": [
                "Да",
                "Нет",
                "Главное меню",
                "Назад"
            ],
            "session_state": {
                "branch": "exit_menu",
                'exit_menu': "",
                'exit_opinion': ""
            }
        }


def what_you_can_def(event):
    return {
        "text":
"""
В этом навыке вы можете предложить песню, а я порекомендую вам подборку похожих,
и вы сможете добавить какие-то из них в раздел "Моя музыка" приложения Яндекс Музыка по желанию.
Кроме того вам доступна сортировка плейлиста Яндекс музыки с вашими понравившимися песнями по жанрам.
Данная функция создаст у вас несколько плейлистов, на которые разделятся ваши любимые песни,
для более удобного поиска песен под настроение.
Также в мои возможности входит перенос музыки из YouTube в приложение Яндекс Музыка.
Если вам понравится какой-либо ремикс/кавер (Или что-либо другое) на какую-либо песню, 
отправив ссылку на видео с этой композицией, вы сможете перенести ее к себе в Яндекс Музыку
""",
        "tts": """В этом навыке вы можете предложить песню, а я порекомендую вам подборку похожих,
и вы сможете добавить какие-то из них в раздел "Моя музыка" приложения Яндекс Музыка по желанию.
Кроме того вам доступна сортировка плейлиста Яндекс музыки с вашими понравившимися песнями по жанрам.
Данная функция создаст у вас несколько плейлистов, на которые разделятся ваши любимые песни,
для более удобного поиска песен под настроение.
Также в мои возможности входит перенос музыки из YouTube в приложение Яндекс Музыка.
Если вам понравится какой-либо ремикс/кавер (Или что-либо другое) на какую-либо песню, 
отправив ссылку на видео с этой композицией, вы сможете перенести ее к себе в Яндекс Музыку
""",
        "buttons": [
            "Главное меню",
            "Назад"
        ],
        "session_state": {
            "branch": "main_menu"
        }
    }


def get_youtube_def(event):
#     return {
#             "text":
#                 """
# Данная функция по какой-то причине не работает при хостинге на Yandex Cloud\n
# Поэтому разработчики уже приступили к переезду на другой хостинг.\n
# Мы сами с нетерпением ждем, как вы сможете воспользоваться этой функцией!
#                 """,
#             "tts": """
#             Данная функция по какой-то причине не работает при хостинге на Yandex Cloud\n
# Поэтому разработчики уже приступили к переезду на другой хостинг.\n
# Мы сами с нетерпением ждем, как вы сможете воспользоваться этой функцией!
#             """,
#             "buttons": [
#                 "Главное меню",
#                 "Назад"
#             ],
#             "session_state": {
#                 "branch": "main_menu",
#             }
#         }
    if 'get_youtube' not in event['state']['session']:
        if 'access_token' in event['state']['user']:
            user_state_update = None
            if 'kind_download' in event['state']['user']:
                kind = event['state']['user']['kind_download']
            else:
                yandex_music_api = YandexMusicApi(event['state']['user']['access_token'])
                yandex_music_api.client.users_playlists_create('download')
                kind = yandex_music_api.client.users_playlists_list()[0]['kind']
            url = f'https://music.yandex.ru/handlers/ugc-upload.jsx?kind={kind}'
            return {
                "text": f"""
Чтобы я смогла перенести музыку, выполните следующее:
Перейдите по ссылке: {url}
Затем скопируйте содержимое на открывшейся странице и отправьте мне
(для быстрого выделения нажмите Ctrl + A, для копирования воспользуйтесь нажатием клавиш Ctrl """,
                "tts": """
Для загрузки видео с YouTube воспользуйтесь устройством с экраном
Чтобы я смогла перенести музыку, выполните следующее:
Перейдите по ссылке:
Затем скопируйте содержимое на открывшейся странице и отправьте мне
(для быстрого выделения нажмите Ctrl + A, для копирования воспользуйтесь нажатием клавиш Ctrl """,
                "buttons": [
                    {
                        'title': 'Ссылка для переноса',
                        'url': url,
                        'hide': False
                    },
                    "Главное меню",
                    "Назад"
                ],
                "session_state": {
                    "branch": "get_youtube",
                    "get_youtube": ""
                },
                "user_state_update": {
                    'kind_download': kind
                }

            }
        else:
            return {
                "text": "Вы не авторизированы, для того, чтобы загрузить видео с YouTube перейдите в главное меню и авторизируйтесь",
                "tts": "Вы не авторизированы, для того, чтобы загрузить видео с YouTube перейдите в главное меню и авторизируйтесь",
                "buttons": [
                    "Главное меню",
                ],
                "session_state": {
                    "branch": "main_menu",
                }
            }
    else:
        if "post_target" not in event['state']['session']:
            response = event["request"]["original_utterance"]
            response = str(response).replace("'", '"')
            first = response.find('https', response.find('post-target'))
            out = response[first: response.find('"', first)]
            return {
                "text": "Отлично! Теперь напишите мне ссылку на видео с YouTube, из которого вы хотите скачать аудио",
                "tts": "Отлично! Теперь напишите мне ссылку на видео с YouTube, из которого вы хотите скачать аудио",
                "buttons": [
                    "Главное меню",
                    "Назад"
                ],
                "session_state": {
                    "branch": "get_youtube",
                    "get_youtube": "",
                    "post_target": out
                }
            }
        else:
            url = event["request"]["original_utterance"]
            post_target = event['state']['session']['post_target']

            def download():
                res = get_info(url)
                print(send_to_yandex(res[1], res[0], post_target))
                print("AAAAAAAAAAAAAAAAAAAAA?")

            th = Thread(target=download)
            th.start()

            return {
                "text": """Музыка успешно перенесена! Скоро она появится в вашей Яндекс Музыке в специально созданном плейлисте.\n
Если этого не произошло, то скорее всего произошла ошибка, которую мы не смогли обработать(""",
                "tts": "Музыка успешно перенесена! Скоро она появится в вашей Яндекс Музыке в специально созданном плейлисте. Если этого не произошло, то скорее всего произошла ошибка, которую мы не смогли обработать(",
                "buttons": [
                    "Главное меню",
                    "Назад"
                ],
                "session_state": {
                    "branch": "main_menu",
                }
            }


find_music = Dialog([], find_music_def, {"найди", "подбери", "похожие", "треки", "произведения", "композиции", "музыку"})
add_song = Dialog([], add_song_def, set({}), always=True)
find_music_completed = TimeoutDialog([add_song], find_music_completed_def, set({}))
sort_playlist = Dialog([], sort_playlist_def, {"отсортируй", "плейлист", "сортируй", "сортировка", "любимые", "раскидай"})
get_youtube = Dialog([], get_youtube_def, {"скачай", "ютуб", "youtube", "загрузи"})
connect_with_developers = Dialog([], connect_with_developers_def, {"связаться", "разработчиками", "создателями", "контакты", "раскидай", "жанрам", "разложи"})
question_developers = Dialog([], question_developers_def, {"задать", "вопрос", "спросить"})
get_access_token = Dialog([], get_access_token_def, {"ввести", "токен"})
authorization = Dialog([get_access_token], authorization_def, {"авторизация", "войти", "авторизуй", "авторизуйся"})
main_menu = StartDialog([find_music, authorization, sort_playlist, get_youtube], main_menu_def, {"главное", "меню", "страница", "главная"})

exit_menu = MiddleWareDialog([], exit_menu_def, {"выход", "выйти", "выйти"})
back = Dialog([], back_def, {"назад", "вернись", "отмена"})
what_you_can = MiddleWareDialog([], what_you_can_def, {'ты', 'умеешь', 'можешь'})
help_menu = MiddleWareDialog([connect_with_developers, question_developers], help_menu_def, {"помощь", "помогите", "хелп", "спасите", "подскажи", "помоги"})

find_music.set_last_state(main_menu)
sort_playlist.set_last_state(main_menu)
get_youtube.set_last_state(main_menu)
get_access_token.set_next_states_list([get_access_token])
get_youtube.set_next_states_list([get_youtube])
add_song.set_next_states_list([add_song])
add_song.set_last_state(main_menu)
find_music.set_next_states_list([find_music, find_music_completed])
connect_with_developers.set_last_state(help_menu)
question_developers.set_last_state(help_menu)
exit_menu.set_next_states_list([exit_menu])
question_developers.set_next_states_list([question_developers])

dialogs_dict = {
    "main_menu": main_menu,
    "find_music": find_music,
    "add_song": add_song,
    "sort_playlist": sort_playlist,
    "get_youtube": get_youtube,
    "find_music_completed": find_music_completed,
    "connect_developers": connect_with_developers,
    "authorization": authorization,
    "get_access_token": get_access_token,
    "question": question_developers,
    "help_menu": help_menu,
    "what_you_can": what_you_can,
    "exit_menu": exit_menu
}
middlewares_list = [
    back,
    help_menu,
    main_menu,
    what_you_can,
    exit_menu
]

music_recomender = MusicRecommender("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")
dialog_handler = Handler(dialogs_dict, middlewares_list, main_menu)


def handler(event, context):
    return dialog_handler.choose_dialog(event)


app = Flask(__name__)


@app.route('/', methods=['POST'])
def hello():
    event = request.get_json()
    response = handler(event, "123")
    print(response)
    print(global_storage)
    return response


if __name__ == "__main__":
    app.run()
