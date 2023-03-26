class Responser:
    def __init__(self, event,  dialog):
        self.dialog = dialog
        self.dialog_type = str(type(self.dialog))[str(type(self.dialog)).index('.') + 1: -2]
        self.event = event

    def get_response(self):
        match self.dialog_type:
            case 'Dialog':
                return self.get_response_dialog()
            case 'MiddleWareDialog':
                return self.get_response_dialog()
            case 'StartDialog':
                return self.get_response_start_dialog()
            case 'TimeoutDialog':
                #Заглушка, так как TimeoutDialog не реализован
                return self.get_response_dialog()

    def get_response_dialog(self):
        dialog_response = self.dialog.get_response_info(self.event)
        return {
            "response": {
                "text": dialog_response["text"],
                "tts": dialog_response["tts"],
                "card": dialog_response["card"] if "card" in dialog_response else None,
                "buttons": self.create_buttons(dialog_response["buttons"]),
                "end_session": dialog_response["end_session"] if "end_session" in dialog_response else False,
            },
            "session": self.event["session"],
            "session_state": dialog_response["session_state"],
            "version": self.event["version"]
        }

    def get_response_start_dialog(self):
        dialog_response = self.dialog.get_response_info(self.event)
        if self.is_authorize():
            return {
                "response": {
                    "text": dialog_response["text"],
                    "tts": dialog_response["tts"],
                    "card": dialog_response["card"] if "card" in dialog_response else None,
                    "buttons": self.create_buttons(dialog_response["buttons"]),
                    "end_session": dialog_response["end_session"] if "end_session" in dialog_response else False,
                },
                "session": self.event["session"],
                "session_state": dialog_response["session_state"],
                "version": self.event["version"]
            }
        else:
            return {
                "start_account_linking": {},
                "session": self.event["session"],
                "version": self.event["version"]
            }

    def create_buttons(self, buttons):
        result = []
        for button in buttons:
            if isinstance(button, str):
                result.append({"title": button, "hide": True})
                continue
            result.append(button)
        return result

    def is_authorize(self):
        return "access_token" in self.event["session"]["user"]
