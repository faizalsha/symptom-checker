import datetime

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from surveys.models import Questionnaire
from surveys.tasks import send_questionnaire_notification_to_company_async, send_mandatory_questionnaire_info_async


@receiver(pre_save, sender=Questionnaire)
def publish_date_update(sender, instance=None, **kwargs):
    """ Method to update publish time if is_published is changes to true. """

    # publishing of new questionnaire
    if instance.id is None:
        if instance.is_published:
            # updating the published_on
            instance.published_on = datetime.datetime.now()

    else:
        questionnaire = Questionnaire.objects.get(id=instance.id)
        if questionnaire.is_published == False and instance.is_published == True:
            # updating the published_on
            instance.published_on = datetime.datetime.now()
            # Sending notifications to the company admins.
            send_questionnaire_notification_to_company_async.delay(
                instance.title,
                instance.id,
                instance.description,
            )


@receiver(post_save, sender=Questionnaire)
def sending_emails_to_companies(sender, instance=None, created=False, **kwargs):
    """ Method to send emails to companies on the publication of the new questionnaire. """

    if created and instance.is_published:
        # Only if the questionnaiure is just created and published.
        send_questionnaire_notification_to_company_async.delay(
            instance.title,
            instance.id,
            instance.description,
        )


@receiver(post_save, sender=Questionnaire)
def sending_emails_for_mandatory_questionnaires(sender, instance=None, created=False, **kwargs):
    """ Method for sending emails to the user about the mandatory questionnaires. """
    if instance.is_published and instance.is_mandatory:
        send_mandatory_questionnaire_info_async.delay(instance.id)
