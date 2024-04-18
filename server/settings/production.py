import os 

# Set debug to False
DEBUG = False

# Set up PostgreSQL Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER_NM'),
        "PASSWORD": os.getenv('DB_USER_PW'),
        "HOST": '35.192.10.144',
        "PORT": 5432,
    }
}