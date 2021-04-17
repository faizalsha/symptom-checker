from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models import Subquery

from django_celery_beat.models import PeriodicTask

from companies.models import Company, Employee, CompanyQuestionnaire, QuestionnaireRule
from companies.tasks import send_company_verification_mail_async


@receiver(pre_save, sender=Company)
def send_verification_confirmation_mail(sender, instance=None, **kwargs):
    """ Method for sending when company is verified from django admin site """
    if instance.id is not None:
        before_state = Company.objects.get(pk=instance.id).is_verified
        after_state = instance.is_verified
        if before_state == False and after_state == True:
            try:
                admin_email = Employee.objects.get(
                    pk=instance.id
                ).user.email
                send_company_verification_mail_async.delay(
                    instance.name, admin_email
                )
            except:
                pass


@receiver(pre_save, sender=CompanyQuestionnaire)
def change_questionnaire_rule_state(sender, instance, **kwargs):
    """ 
    Callback method for changing QuestionnaireRule's PeriodicTask's state (i.e enabled)
    depending upon the new state of CompanyQuestionnaire object
    """
    if instance.id is not None:
        before_state = CompanyQuestionnaire.objects.get(
            id=instance.id
        ).currently_active

        after_state = instance.currently_active

        if before_state != after_state:
            PeriodicTask.objects.filter(
                questionnairerule__in=Subquery(
                    QuestionnaireRule.objects.filter(
                        company_questionnaire_id=instance.id
                    ).values_list('id', flat=True)
                )
            ).update(enabled=after_state)
