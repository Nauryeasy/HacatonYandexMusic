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
                middleware_dialog.set_last_state(self.get_state(event))
                responser = Responser(event, middleware_dialog)
                return responser.get_response()

        trigger_dialogs = self.dialogs_dict[self.get_state(event)].next_states_list

        for dialog in trigger_dialogs:
            if self.check_tokens(event, dialog):
                responser = Responser(event, dialog)
                return responser.get_response()

    @staticmethod
    def get_state(event):
        return event['state']['session']['branch']

    @staticmethod
    def check_tokens(event, dialog):
        return dialog.tokens & set(event['request']["nlu"]['tokens'])

    @staticmethod
    def check_new_session(event):
        return event['session']['new'] or not "branch" in event["state"]["session"]
