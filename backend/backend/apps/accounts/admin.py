from django.contrib import admin
from django.contrib.auth.models import Group

from accounts.models import User
from commons.admin import CommonAdmin

# Unregistering unused Group Model
admin.site.unregister(Group)


# Registering User model
@admin.register(User)
class UserAdmin(CommonAdmin):
    exclude = ('groups', 'user_permissions')
    list_display = ('first_name', 'is_email_verified', 'is_active')
    list_filter = ('is_email_verified', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-updated_at',)

    def save_model(self, request, obj, form, change):
        """ Method for saving the User instance with setting hashed password. """
        if obj.id is None:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
