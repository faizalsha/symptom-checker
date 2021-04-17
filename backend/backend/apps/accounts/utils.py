import jwt

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags


def send_account_verification_email(email, token):
    """ Method to send the Email to the user. """

    link = reverse_lazy('accounts:email-verify', kwargs={'token': token})
    base = settings.FRONTEND_IP

    html_content = render_to_string(
        'email_verify.html', {'link': f'{base}{link}'})
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        'Confirm your Email Id for activating you account',
        text_content,
        settings.EMAIL_HOST_USER,
        [email]
    )

    email.attach_alternative(html_content, 'text/html')
    email.send()


def send_password_reset_email(email, token):
    """ Method to send the Email to the user. """

    link = reverse_lazy('accounts:reset')
    base = settings.FRONTEND_IP

    html_content = render_to_string(
        'email_reset.html', {'link': f'{base}{link}{token}'})
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        'Reset your Symptom Checker password',
        text_content,
        settings.EMAIL_HOST_USER,
        [email]
    )

    email.attach_alternative(html_content, 'text/html')
    email.send()


def send_welcome_msg_with_questionnaire(name, email, questionnaires):
    """ Method for sending welcome msg with mandatory questionnsires. """

    base = settings.FRONTEND_IP
    links = [
        (
            f'{base}{reverse_lazy("surveys:questionnaire-detail", kwargs={"pk": questionnaire["id"]})}',
            questionnaire['title']
        )
        for questionnaire in questionnaires
    ]

    html_content = render_to_string(
        "email_welcome.html", {"links": links, 'name': name}
    )
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        "Welcome to Symptom Checker",
        text_content, settings.EMAIL_HOST_USER,
        [email]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()


class TokenGenerator:
    """ Class for Generating JWT token and decode them. """

    secret = settings.SECRET_KEY

    @ classmethod
    def generate_token(cls, user, algorithm_used='HS256', **kwargs):
        """ Method for generating token. """

        payload = {
            'email': user.email,
        }
        payload.update(kwargs)

        token = jwt.encode(payload, cls.secret, algorithm=algorithm_used)
        return token

    @classmethod
    def decode_token(cls, token, algorithms_used=['HS256'], **kwargs):
        """ Method for decoding token. """
        try:
            return jwt.decode(token, cls.secret, algorithms=algorithms_used, **kwargs)
        except:
            return None
