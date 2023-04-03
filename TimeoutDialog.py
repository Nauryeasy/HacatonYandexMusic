from Dialog import Dialog
from globalStorage import *
import threading


class TimeoutDialog(Dialog):
    def get_response_info(self, event):
        print(global_storage)
        if not self.get_user_id(event) in global_storage:
            set_key(global_storage, self.get_user_id(event), {'response': {}, 'isCompleted': False})
            th = threading.Thread(target=self.get_timeout_response, args=(event, ), daemon=True)
            th.start()
            return {
                "text": "Загрузка",
                "tts": "Загрузка. Для того, чтобы проверить не появился ли результат скажите: Проверить",
                "buttons": ["Проверить"],
                "session_state": event["state"]["session"]
            }
        else:
            if not get_key(global_storage, self.get_user_id(event))['isCompleted']:
                return {
                    "text": "Все еще загрузка",
                    "tts": "Все еще загрузка. Для того, чтобы проверить не появился ли результат скажите: Проверить",
                    "buttons": ["Проверить"],
                    "session_state": event["state"]["session"]
                }
            else:
                response = get_key(global_storage, self.get_user_id(event))['response']
                del global_storage[self.get_user_id(event)]
                return response

    def get_timeout_response(self, event):
        response = self.get_response(event)
        set_key(global_storage, self.get_user_id(event), {"response": response, 'isCompleted': True})

    @staticmethod
    def get_user_id(event):
        return event['session']['application']['application_id']