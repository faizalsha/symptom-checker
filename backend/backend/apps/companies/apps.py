from django.apps import AppConfig


class CompaniesConfig(AppConfig):
    name = 'companies'

    def ready(self):
        """ Importing Signals. """
        import companies.signals
