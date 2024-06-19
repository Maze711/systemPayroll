from time import *

class ListFunction:
    def __init__(self, main_window):
        self.main_window = main_window

    def timeClock(self):
        time_format = strftime("%I:%M:%S %p")
        self.main_window.lblTime.setText(time_format)

        date_format = strftime("%A, %B %d, %Y")
        self.main_window.lblDate.setText(date_format)