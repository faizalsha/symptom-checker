from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags


def send_invite_email(sender, receiver, receiver_email, token):
    """ Method to send the Email to the user. """

    link = reverse_lazy('commons:accept-invite')
    base = settings.FRONTEND_IP

    html_content = render_to_string(
        'email_invite.html',
        {
            'link': f'{base}{link}{token}',
            'sender': sender,
            'receiver': receiver
        }
    )
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        'Invitation for joining Symptom Checker',
        text_content,
        settings.EMAIL_HOST_USER,
        [receiver_email]
    )

    email.attach_alternative(html_content, 'text/html')
    email.send()
