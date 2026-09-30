"""
Entry point for the Biomedical Waste Robot desktop application.

The app always starts at the admin login screen. Only a successful login
opens the Dashboard; anyone can still submit a complaint from the login
screen without logging in.
"""

from gui.login import LoginWindow
from gui.dashboard import Dashboard


def main():
    login = LoginWindow()
    login.mainloop()

    if login.authenticated:
        app = Dashboard()
        app.mainloop()


if __name__ == "__main__":
    main()
