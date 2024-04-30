import os 

from .base import *

if os.getenv('PIPELINE') == 'production':
    from .production import *
else:
    from .local import *