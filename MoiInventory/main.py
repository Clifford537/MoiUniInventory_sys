# main.py
import os
import sys
from django.core.management import execute_from_command_line

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoiInventory.settings')

def run():
    # You may need to modify sys.argv if necessary
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    run()
