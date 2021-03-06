from backend.settings.base import Base


class Dev(Base):

    import environ

    # reading content of environ file
    env = environ.Env()
    environ.Env.read_env()

    DEBUG = True

    # Database
    # https://docs.djangoproject.com/en/2.2/ref/settings/#databases

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env.str('DB_NAME'),
            'USER': env.str('DB_USER'),
            'PASSWORD': env.str('DB_PASSWORD'),
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

    # Celery settings

    # Using Redis as Message Broker.

    CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    FRONTEND_IP = 'http://localhost:3000'
