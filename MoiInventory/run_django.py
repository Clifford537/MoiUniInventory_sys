import os
import sys
import webbrowser

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MoiInventory.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Start the Django development server without autoreload
    execute_from_command_line(['manage.py', 'runserver', '--noreload'])

    # Open the default web browser to the Django server's address
    webbrowser.open("http://127.0.0.1:8000")
