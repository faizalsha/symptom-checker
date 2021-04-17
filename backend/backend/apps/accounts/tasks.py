from celery import shared_task

from accounts.utils import (send_account_verification_email,
                            send_password_reset_email,
                            send_welcome_msg_with_questionnaire)

from surveys.models import Questionnaire


@shared_task
def send_account_verification_email_async(email, token):
    """" Asynchronous Task to send account verification email. """
    send_account_verification_email(email, token)


@shared_task
def send_password_reset_email_async(email, token):
    """ Asynchronous Task to send forget password email. """
    send_password_reset_email(email, token)


@shared_task
def send_welcome_msg_with_questionnaire_async(name, email):
    """ Asynchronous task to send welcome msg with mandatory questionnaires. """
    questionnaires = Questionnaire.objects.filter(
        is_published=True, is_mandatory=True
    ).values('id', 'title')
    send_welcome_msg_with_questionnaire(name, email, questionnaires)
