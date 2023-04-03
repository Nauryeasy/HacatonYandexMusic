from Response import Responser


class Handler:
    def __init__(self, dialogs_dict, middleware_dialog_list, start_dialog):
        self.dialogs_dict = dialogs_dict
        self.middleware_dialog_list = middleware_dialog_list
        self.start_dialog = start_dialog

    def choose_dialog(self, event):
        if self.check_new_session(event):
            responser = Responser(event, self.start_dialog)
            return responser.get_response()

        for middleware_dialog in self.middleware_dialog_list:
            if self.check_tokens(event, middleware_dialog):
                middleware_dialog.set_last_state(self.dialogs_dict[self.get_state(event)])
                if middleware_dialog.last_state == middleware_dialog:
                    middleware_dialog.set_last_state(self.start_dialog)
                responser = Responser(event, middleware_dialog)
                return responser.get_response()

        trigger_dialogs = self.dialogs_dict[self.get_state(event)].next_states_list

        for dialog in trigger_dialogs:
            keys = list(self.dialogs_dict.keys())
            values = list(self.dialogs_dict.values())
            if self.check_tokens(event, dialog) or dialog.always or keys[values.index(dialog)] in event['state']['session']:
                responser = Responser(event, dialog)
                return responser.get_response()

        return {
            "response": {
                "text": "Простите, не смогла распознать вашу команду\n"
                        "Повторите еще раз или обратитесь в помощь или в 'Что ты умеешь'",
                "tts": "Простите, не смогла распознать вашу команду" 
                        "Повторите еще раз или обратитесь в помощь или в 'Что ты умеешь'",
                "card": None,
                "buttons": Responser.create_buttons(['Помощь', 'Что ты умеешь']),
                "end_session": False
            },
            "session": event["session"],
            "session_state": event['state']['session'],
            "version": event["version"]
        }

    @staticmethod
    def get_state(event):
        return event['state']['session']['branch']

    @staticmethod
    def check_tokens(event, dialog):
        return dialog.tokens & set(event['request']["nlu"]['tokens'])

    @staticmethod
    def check_new_session(event):
        return event['session']['new'] or not "branch" in event["state"]["session"]
