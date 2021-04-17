from django.contrib import admin
from commons.models import Invite

from commons.models import Invite


class CommonAdmin(admin.ModelAdmin):
    """ Base Model Admin for all models. """

    def delete_model(self, request, obj):
        """ Stopping softdelete method from being run. 
            Instead permanet delete should run .
        """
        obj.permanent_delete()

# Registering Invite Model to the user.


@admin.register(Invite)
class InviteAdmin(CommonAdmin):
    list_display = ('sender', 'receiver', 'invite_status', 'is_active')
    list_filter = ('invite_status',)
    search_fields = ('sender', 'receiver')
    ordering = ('updated_at',)
