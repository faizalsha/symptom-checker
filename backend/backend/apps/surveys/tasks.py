from django.contrib.auth import get_user_model
from celery import shared_task

from companies.models import Employee
from surveys.utils import send_questionnaire_notification_to_company, send_mandatory_questionnaire_info
from surveys.models import Questionnaire

AUTH_USER = get_user_model()


@shared_task
def send_questionnaire_notification_to_company_async(title, id, description):
    """ Sending Company admins information about newly added questionnaire. """

    # Getting all the active company admins.
    company_admins = Employee.objects.filter(
        is_company_admin=True
    ).values_list('user__email', flat=True)

    # Sending mail to all the company admins
    send_questionnaire_notification_to_company(
        company_admins, title, id, description
    )


@shared_task
def send_mandatory_questionnaire_info_async(questionnaireId):
    """ Async task for sending email for mandatory question to the users. """
    user_emails = AUTH_USER.objects.all().values_list('email', flat=True)
    questionnaire = Questionnaire.objects.get(id=questionnaireId)
    try:
        send_mandatory_questionnaire_info(
            user_emails, questionnaireId, questionnaire.title,
            questionnaire.description
        )
    except Exception as e:
        pass
