from backend.settings.base import Base


class Prod(Base):

    DEBUG = False

    ALLOWED_HOSTS = ['*']

    # Database
    # https://docs.djangoproject.com/en/2.2/ref/settings/#databases

    DATABASES = {
        'default': {
            'ENGINE': '',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }

    # celery settings

    CELERY_BROKER_URL = ''
    CELERY_RESULT_BACKEND = ''
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # EMAIL_HOST = 'smtp.gmail.com'
    # EMAIL_HOST_USER = 'example@gmail.com'
    # EMAIL_HOST_PASSWORD = '----------------' #paste the key or password app here
    # EMAIL_PORT = 587
    # EMAIL_USE_TLS = True
    # DEFAULT_FROM_EMAIL = 'default from email'
