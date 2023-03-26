from Dialog import Dialog


class StartDialog(Dialog):
    def __init__(self, next_states_list, get_response, tokens):
        super().__init__(next_states_list, get_response, tokens)
        self.last_state = self
