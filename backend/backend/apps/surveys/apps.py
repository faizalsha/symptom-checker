from django.apps import AppConfig


class SurveysConfig(AppConfig):
    name = 'surveys'

    def ready(self):
        """ Importing signals. """
        import surveys.signals
