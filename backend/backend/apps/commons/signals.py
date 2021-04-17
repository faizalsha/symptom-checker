from django.dispatch import receiver
from django.db.models.signals import post_save

from commons import models as commons_models
from commons.tasks import send_invite_email_asyc


@receiver(post_save, sender=commons_models.Invite)
def send_invite_email_to_receiver(sender, instance=None, created=False, **kwargs):
    """ Method for sending invite emails to the receiver of invite. """
    if created and instance.invite_status == instance.SENT:
        send_invite_email_asyc.delay(
            instance.sender.get_full_name(), instance.receiver.get_full_name(),
            instance.receiver.email, instance.invite_token
        )
