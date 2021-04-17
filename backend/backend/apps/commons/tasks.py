from celery import shared_task

from commons.utils import send_invite_email
from commons.models import Invite


@shared_task
def send_invite_email_asyc(sender, receiver, receiver_email, token):
    """ Sending email to reciever Asynchronously. """
    invite = Invite.objects.get(receiver__email=receiver_email)
    try:
        send_invite_email(sender, receiver, receiver_email, token)
        invite.change_invite_status(Invite.SENT)
    except Exception as e:
        invite.change_invite_status(Invite.SENT_FAILED)
