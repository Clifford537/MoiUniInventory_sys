# gui.py

import os
import threading
from flaskwebgui import FlaskUI
from django.core.wsgi import get_wsgi_application
from waitress import serve

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoiInventory.settings')

application = get_wsgi_application()

def run_server():
    serve(application, host='0.0.0.0', port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    FlaskUI(app=application, server="django").run()
