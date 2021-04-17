from django.db import models

from commons.querysets import SoftDeleteQuerySet


class PermanentDeleteManager(models.Manager):
    """ Manager to handle permanent deletion of objects. """
    pass


class SoftDeleteManager(models.Manager):
    """ Manager to handle objects soft deletion. """

    def get_queryset(self):
        """ Method to get queryset based on active only flag. """
        return SoftDeleteQuerySet(self.model).filter(is_active=True)

    def permanent_delete(self):
        """ Method for deleting objects completely from database. """
        return self.get_queryset().permanent_delete()
