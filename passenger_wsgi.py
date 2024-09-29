import os
import sys

# Insert the application's path into the system path
sys.path.insert(0, os.path.dirname(__file__))

# Import the WSGI application from the Django project
from cenartechpro.wsgi import application