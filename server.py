#!/usr/bin/env python3
import os
import sys
from django.core.management import execute_from_command_line
from django.conf import settings

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'password_manager.settings')

def start_django_server():
    # Execute the Django server command with the desired port (e.g., 8000)
    execute_from_command_line(['manage.py', 'runserver', '3000'])

if __name__ == '__main__':
    # Perform any necessary setup before starting the server
    
    # For example, you can add custom logic here
    
    # Start the Django server
    start_django_server()
