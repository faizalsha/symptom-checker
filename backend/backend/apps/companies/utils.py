import binascii
import os
import random
import string

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags

from commons import constants as commons_constant

from commons.constants import DEFAULT_TOKEN_LENGTH, DEFAULT_RANDOM_STRING_LENGTH


def generate_token(len=DEFAULT_TOKEN_LENGTH):
    """ Method to get random string to be used as token """
    return binascii.hexlify(os.urandom(len)).decode()


def generate_random_string(len=DEFAULT_RANDOM_STRING_LENGTH):
    """ Method to generate random string of given length"""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(len))


def partially_hide_string(input):
    """ 
    Method to replace alternative charcter with `*` 
    (e.g.) used in partially hiding email address
    """
    res = ['*' if not idx % 2 else ele.lower()
           for idx, ele in enumerate(input)
           ]
    return "".join(res)


def send_company_invite_email(email, token, **kwargs):
    """ Method for sending company invite email """

    link = f'/company-invite/{token}'
    base = settings.FRONTEND_IP
    html_content = None

    if 'password' not in kwargs:
        html_content = render_to_string(
            'company_invite.html', {'link': f'{base}{link}'}
        )
    else:
        html_content = render_to_string(
            'company_invite_with_credentials.html', {
                'link': f'{base}{link}', 'password': kwargs['password']
            }
        )
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        'Invitation for company joining on symptom checker',
        text_content,
        settings.EMAIL_HOST_USER,
        [email]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


def send_company_verification_email(name, email, **kwargs):
    """ Method for sending company verification confirmation email """
    html_content = render_to_string(
        'company_verification.html', {'company_name': name}
    )

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        'Confirmation for company verification',
        text_content,
        settings.EMAIL_HOST_USER,
        [email]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


def send_company_questionnaire_notification(emails, company_id, questionnaire_id):
    """ Method for sending questionnaire notification email """

    base = settings.FRONTEND_IP
    link = f'{base}/surveys/company/{company_id}/questionnaire/{questionnaire_id}'
    html_content = render_to_string(
        'questionnaire_notification.html', {'link': link}
    )
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        'Questionnaire notification',
        text_content,
        settings.EMAIL_HOST_USER,
        emails
    )

    email.attach_alternative(html_content, 'text/html')
    email.send()
