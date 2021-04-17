from celery import shared_task

from companies.utils import (send_company_invite_email,
                             send_company_verification_email,
                             send_company_questionnaire_notification)
from companies.models import CompanyInvite


@shared_task
def send_company_invite_email_async(email, token, **kwargs):
    """ 
    Celery task for sending company invite email 
    and also updating status of invite from PENDING -> SENT or PENDING -> SENT_FAILED
    """
    invite = CompanyInvite.objects.get(token=token)
    try:
        send_company_invite_email(email, token, **kwargs)
        invite.change_invite_status(CompanyInvite.SENT)
    except:
        invite.changeInviteStatus(CompanyInvite.SENT_FAILED)


@shared_task
def send_company_verification_mail_async(company_name, admin_email, **kwargs):
    try:
        send_company_verification_email(company_name, admin_email, **kwargs)
    except:
        pass


@shared_task
def send_company_questionnaire_notification_async(emails, company_id, questionnaire_id):
    """ Celery task for sending questionnaire notification to all employee """
    send_company_questionnaire_notification(
        emails,
        company_id,
        questionnaire_id
    )
