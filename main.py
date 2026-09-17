"""
Entry point for the Biomedical Waste Robot desktop application.

Before running:
  1. Create the MySQL database and load database/schema.sql (+ seed_data.sql)
     - easiest way: python setup_db.py  (uses the same driver as the app,
       no mysql.exe / PATH setup needed)
  2. Update config/config.py with your MySQL credentials
  3. pip install -r requirements.txt

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
