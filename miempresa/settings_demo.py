"""Vista previa explícita sin credenciales. EV3 debe usar settings y MySQL."""
from .settings import *  # noqa

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'demo.sqlite3'}}
