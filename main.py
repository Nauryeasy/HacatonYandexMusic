from flask import Flask, request
from Dialog import Dialog
from Handler import Handler
from Response import Responser
from StartDialog import StartDialog
from TimeoutDialog import TimeoutDialog
from MiddlewareDialog import MiddleWareDialog


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
Вы открыли раздел 'Помощь'.\n
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


find_music = Dialog([], find_music_def, {"найди", "песню"})
main_menu = StartDialog([find_music], main_menu_def, {"главное", "меню"})
connect_with_developers = Dialog([], connect_with_developers_def, {"связаться", "разработчиками"})
skills = Dialog([], skills_def, {"возможности"})
question_developers = Dialog([], question_developers_def, {"задать", "вопрос"})

back = Dialog([], back_def, {"назад"})
help_menu = MiddleWareDialog([connect_with_developers, skills, question_developers], help_menu_def, {"помощь"})

find_music.set_last_state(main_menu)
connect_with_developers.set_last_state(help_menu)
skills.set_last_state(help_menu)
question_developers.set_last_state(help_menu)

dialogs_dict = {
    "main_menu": main_menu,
    "find_music": find_music,
    "connect_developers": connect_with_developers,
    "skills": skills,
    "question": question_developers,
    "help_menu": help_menu
}
middlewares_list = [
    back,
    help_menu
]

dialog_handler = Handler(dialogs_dict, middlewares_list, main_menu)


def handler(event, context):
    return dialog_handler.choose_dialog(event)


app = Flask(__name__)


@app.route('/', methods=['POST'])
def hello():
    event = request.get_json()
    response = handler(event, "123")
    print(response)
    return response


if __name__ == "__main__":
    app.run()
