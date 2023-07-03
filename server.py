#!/usr/bin/env python3
import os
import sys
from django.core.management import execute_from_command_line
from django.conf import settings

from sqlite3 import dbapi2 as Database
print(Database.sqlite_version_info)

'''# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'password_manager.settings')

def make_migrations():
    # Execute the Django's makemigrations command
    execute_from_command_line(['manage.py', 'makemigrations'])

def start_django_server():
    # Execute the Django server command with the desired port (e.g., 8000)
    execute_from_command_line(['manage.py', 'runserver', '3000'])

if __name__ == '__main__':
    # Perform any necessary setup before making migrations
    # For example, you can add custom logic here

    # Make the migrations
    make_migrations()'''

    # Start the Django server
    start_django_server()

