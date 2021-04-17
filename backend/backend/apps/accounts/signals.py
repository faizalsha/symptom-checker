from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from rest_framework.authtoken.models import Token

from accounts.models import User
from accounts.tasks import send_welcome_msg_with_questionnaire_async
from surveys.models import Questionnaire


@receiver(post_save, sender=User)
def create_token(sender, instance=None, created=False, **kwargs):
    """ Method that creates token if a new user is created. """
    if created:
        Token.objects.create(user=instance)


@receiver(pre_save, sender=User)
def send_welcome_email(sender, instance=None, **kwargs):
    """ Method for sending welcome msg and links to mandatory questionnaires to fill. """
    if instance.id is not None:
        before_state = User.objects.get(id=instance.id).is_email_verified
        after_state = instance.is_email_verified
        if after_state == True and before_state == False:
            send_welcome_msg_with_questionnaire_async.delay(
                instance.get_full_name(), instance.email
            )
