import binascii
import os

from django.conf import settings
from django.db import models

from commons import constants as commons_constants
from commons.manager import SoftDeleteManager, PermanentDeleteManager

# Getting the user model used by the Django.
AUTH_USER = settings.AUTH_USER_MODEL


class CommonBaseModel(models.Model):
    """ Abstract Base Model for other models having
        is_active, created_at, updated_at fields. 

        Also Having capabilities of soft_deleting an object.
    """

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager for accessing objects same as normal Manager(models.Manager).
    all_objects = PermanentDeleteManager()
    # Manager for Solt deletion operation.
    objects = SoftDeleteManager()

    def delete(self):
        """ Method for soft deleting the object. """
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    def permanent_delete(self):
        """ Method for permanently deleting the object. """
        super(CommonBaseModel, self).delete()

    class Meta:
        # Marking abstract equals to True for making it an abstract model.
        abstract = True


class Invite(CommonBaseModel):
    """ Model Definition of Invite. """

    # Constants for Invite statuses.
    SENT = 0
    SENT_FAILED = 1
    ACCEPTED = 2
    CANCELLED = 3
    PENDING = 4

    # Choices for Invite statuses.
    INVITE_STATUS_CHOICES = (
        (SENT, 'SENT'),
        (SENT_FAILED, 'SENT_FAILED'),
        (ACCEPTED, 'ACCEPTED'),
        (CANCELLED, 'CANCELLED'),
        (PENDING, 'PENDING'),
    )

    # User sending invite.
    sender = models.ForeignKey(
        AUTH_USER,
        related_name='sent_invites',
        on_delete=models.CASCADE
    )

    # User who will receive invite.
    receiver = models.ForeignKey(
        AUTH_USER,
        related_name='recieved_invites',
        on_delete=models.CASCADE
    )

    # status of the invite.
    invite_status = models.IntegerField(
        choices=INVITE_STATUS_CHOICES, default=SENT
    )

    # Token to be used for user invitation
    invite_token = models.CharField(
        max_length=commons_constants.DEFAULT_TOKEN_LENGTH,
        unique=True
    )

    def change_invite_status(self, status):
        """ Method for changing status of the invite. """
        self.invite_status = status
        self.save(update_fields=['invite_status', 'updated_at'])

    def __str__(self):
        """ Unicode representation of Invite model. """
        return f'{self.sender.get_full_name()} - invited - {self.receiver.get_full_name()}'

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.invite_token = self.generate_key()
        return super().save(*args, **kwargs)
