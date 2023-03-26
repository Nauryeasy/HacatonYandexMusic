from Dialog import Dialog
from Handler import Handler
from Response import Responser
from StartDialog import StartDialog
from TimeoutDialog import TimeoutDialog


def find_music_def(event):
    return {
        "text": "Напишите название песни:",
        "tts": "Напишите название песни",
        "buttons": [],
        "session_state": {
            "branch": "find_music"
        }
    }


def main_menu_def(event):
    return {
        "text": "Главное меню",
        "tts": "Главное меню",
        "buttons": [
            "Найди песню",
            "Отсортируй плейлист",
            "Добавь с YouTube",
            "Помощь",
            "Что ты умеешь"
        ],
        "session_state": {
            "branch": "main_menu"
        }
    }


def back_def(event):
    return dialog_handler.dialogs_dict[dialog_handler.get_state(event)].last_state.get_response_info(event)


def help_menu_def(event):
    return {
        "text": """
Вы открыли раздел 'Помощь'.\n"
Здесь я могу подробно рассказать про свои возможности.\n
Также вы можете задать вопрос разработчикам навыка или узнать, как связаться с ними.
                """,
        "tts": "Вы открыли раздел 'Помощь'. Здесь я могу подробно рассказать про свои возможности. Также вы можете задать вопрос разработчикам навыка или узнать, как связаться с ними.",
        "buttons": [
            "Как связаться с разработчиками?",
            "Расскажи про возможности",
            "Задать вопрос",
            "Что ты умеешь",
            "Назад"
        ],
        "session_state": {
            "branch": "help_menu"
        }
    }


def connect_with_developers_def(event):
    return {
        "text": "*Контакты разработчиков*",
        "tts": "ЗАЗАЗАЗАЗАЗАЗААЗАЗЗА",
        "buttons": [
            "Главное меню",
            "Назад"
        ],
        "session_state": {
            "branch": "connect_developers"
        }
    }


def skills_def(event):
    return {
        "text": """
В этом навыке вы можете найти похожие песни, которую вы предложите. \n
Я порекомендую вам подборку похожих песен, и вы сможете добавить их в раздел "Моя музыка" приложения Яндекс музыка по вашей просьбе.
Кроме того, я могу отсортировать плейлисты по жанрам и перенести понравившуюся музыку из You Tube в Яндекс музыку.
""",
        "tts": "В этом навыке вы можете найти похожие песни, которую вы предложите. Я порекомендую вам подборку похожих песен, и вы сможете добавить их в раздел 'Моя музыка' приложения Яндекс музыка по вашей просьбе. Кроме того, я могу отсортировать плейлисты по жанрам и перенести понравившуюся музыку из You Tube в Яндекс музыку.",
        "buttons": [
            "Главное меню",
            "Назад"
        ],
        "session_state": {
            "branch": "skills"
        }
    }


def question_developers_def(event):
    return {
        "text": "Напишите ваш вопрос:",
        "tts": "Напишите ваш вопрос",
        "buttons": [
            "Главное меню",
            "Назад"
        ],
        "session_state": {
            "branch": "question"
        }
    }
