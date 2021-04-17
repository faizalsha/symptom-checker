from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags


def send_mandatory_questionnaire_info(user_emails, id, title, description):
    """ Method to send the Email to the user about the mandatory questionnaires. """

    link = reverse_lazy('surveys:questionnaire-detail', kwargs={'pk': id})
    base = settings.FRONTEND_IP

    html_content = render_to_string(
        'email_mandatory_questionnaire_info.html',
        {
            'link': f'{base}{link}',
            'title': title,
            'description': description
        }
    )
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        'New Mandatory Questionnaire',
        text_content,
        settings.EMAIL_HOST_USER,
        user_emails
    )

    email.attach_alternative(html_content, 'text/html')
    email.send()


def send_questionnaire_notification_to_company(company_admins_email, title, id, description):
    """ Method to send the Email to the companies about new questionnaire. """

    link = reverse_lazy('surveys:questionnaire-detail', kwargs={'pk': id})
    base = settings.FRONTEND_IP

    html_content = render_to_string(
        'email_questionnaire_info.html',
        {
            'link': f'{base}{link}',
            'title': title,
            'description': description
        }
    )
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        'New Questionnaire Added',
        text_content,
        settings.EMAIL_HOST_USER,
        company_admins_email
    )

    email.attach_alternative(html_content, 'text/html')
    email.send()
