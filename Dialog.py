class Dialog:
    def __init__(self, next_states_list, get_response, tokens, last_state=None):
        self.next_states_list = next_states_list
        self.get_response = get_response
        self.last_state = last_state
        self.tokens = tokens

    def get_response_info(self, event):
        return self.get_response(event)

    def set_last_state(self, last_state):
        self.last_state = last_state
