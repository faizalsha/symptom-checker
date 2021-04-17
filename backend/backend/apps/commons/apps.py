from django.apps import AppConfig


class CommonsConfig(AppConfig):
    name = 'commons'

    def ready(self):
        """ Importing Signals. """
        import commons.signals
