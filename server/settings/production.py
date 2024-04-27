import os 

# Set debug to False
DEBUG = True

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

# settings.py
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)