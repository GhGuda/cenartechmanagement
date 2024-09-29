import os
import sys

from django.core.wsgi import get_wsgi_application
from urllib.parse import unquote


sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cenartechpro.settings')

SCRIPT_NAME = os.getcwd()

class PassengerPathInfoFix:
    """
    Sets PATH_INFO from REQUEST_URI because Passenger doesn't provide it.
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = unquote(environ.get('SCRIPT_NAME', ''))
        request_uri = environ.get('RAW_URI', environ.get('REQUEST_URI', ''))
        if request_uri:
            request_uri = unquote(request_uri)
            offset = request_uri.startswith(script_name) and len(script_name) or 0
            environ['PATH_INFO'] = request_uri[offset:].split('?', 1)[0]
        return self.app(environ, start_response)


application = get_wsgi_application()
application = PassengerPathInfoFix(application)

