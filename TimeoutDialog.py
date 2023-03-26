from Dialog import Dialog
from globalStorage import *


class TimeoutDialog(Dialog):
    def get_response_info(self, event):
        return self.get_response(event)
