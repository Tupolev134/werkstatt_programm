import sys

from PyQt6.QtWidgets import QApplication


class ApplicationWindowManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.current_window = None
        self.windows = {}  # Dictionary to hold window names and their corresponding classes.
        self.history = []  # List to hold the navigation history.
        self.current_index = -1  # Current position in the navigation history.

    def add_window(self, name, window_class):
        self.windows[name] = window_class

    def start(self):
        self.show_window('main_menu')
        sys.exit(self.app.exec())

    def show_window(self, name, *args, **kwargs):
        if name not in self.windows:
            return
        if self.current_window is not None:
            self.current_window.close()

        # Pass self (the window manager) to the window class
        self.current_window = self.windows[name](self, *args, **kwargs)
        self.current_window.show()

        # Update the navigation history.
        self.history = self.history[:self.current_index+1]  # Remove forward history if any.
        self.history.append(name)
        self.current_index += 1

    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            window_name = self.history[self.current_index]
            self.show_window(window_name)

    def go_forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            window_name = self.history[self.current_index]
            self.show_window(window_name)
