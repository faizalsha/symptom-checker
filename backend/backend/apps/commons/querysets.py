from django.db.models import QuerySet


class SoftDeleteQuerySet(QuerySet):
    """ Custom Queryset class for SoftDelete Manager. """

    def delete(self):
        """ Method to soft delete the queryset. """

        # This method updates the is_active value of the model to False.
        # Hence it can be regarded as Deleted.
        return super(SoftDeleteQuerySet, self).update(is_active=False)

    def permanent_delete(self):
        """ Method to delete queryset completely. """

        # This method actually deletes the objects from the database.
        return super(SoftDeleteQuerySet, self).delete()
