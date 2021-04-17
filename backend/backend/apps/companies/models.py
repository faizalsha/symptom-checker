from django.conf import settings
from django.contrib.postgres.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django_celery_beat.models import PeriodicTask

from commons import constants as commons_constant
from commons.models import CommonBaseModel
from commons.validators import PhoneNumberValidator
from surveys.models import Questionnaire
from companies.utils import generate_token

# Getting the User Model used by the Django.
AUTH_USER = settings.AUTH_USER_MODEL


class Company(CommonBaseModel):

    """ Model Definition of Company. 

        Model Fields Include:-
        1. name: Name of the company,
        2. address: address of the company,
        3. city: city in which company's main office is located,
        4. state: state in which company's main office is located,
        5. pincode: area pincode of the company,
        6. registeration_date: Date on which this company is registered,
        7. phone: contact number of the company,
        8. about: text describing the company,
        9. logo: Company's logo.
        10. is_verified: Boolean denoting whether this company is verified or not. 
    """

    # name should be unique.
    name = models.CharField(
        max_length=commons_constant.COMPANY_NAME_MAX_LENGTH,
        unique=True
    )
    address = models.TextField()
    city = models.CharField(max_length=commons_constant.MAX_LENGTH)
    state = models.CharField(max_length=commons_constant.MAX_LENGTH)
    pincode = models.CharField(max_length=commons_constant.MAX_LENGTH)
    registration_date = models.DateField(auto_now=True)

    phone = models.CharField(
        max_length=commons_constant.PHONE_NUMBER_LENGTH,
        validators=[PhoneNumberValidator],
    )
    about = models.TextField()
    logo = models.ImageField(upload_to="company_logos", blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        """ Unicode Representation of Company Model. """
        return f'{self.name}'


class Employee(CommonBaseModel):
    """ Model Definition of Employee. 

        Model Fields Include:-
        1. user: User which is the employee.
        2. company: Company to which this employee object belongs to.
        3. is_company_admin: Boolean to check if the employee is also a company admin.
    """

    # TODO: Handling case for soft deleting this model on deletion of User

    user = models.ForeignKey(
        AUTH_USER,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    is_company_admin = models.BooleanField(default=False)

    def __str__(self):
        """ Unicode Representation for Employee Model. """
        return f'{self.company.name} - {self.user.first_name}'

    class Meta:
        ordering = ['-created_at']


class CompanyAdvice(CommonBaseModel):
    """ Model Definition for Company Advices. 

        Model Fields Include:-
        1. company: Company which is giving advice.
        2. text: Advice text which is given by the company.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company_advices'
    )
    admin = models.ForeignKey(
        AUTH_USER,
        on_delete=models.CASCADE,
        related_name='company_advices',
        null=True
    )
    text = models.TextField()

    def __str__(self):
        """ Unicode Representation for Company Advices Model. """
        return f'{self.company.name}'


class CompanyQuestionnaire(CommonBaseModel):
    """  Model Definition of CompanyQuestionnaire. 

        Model Fields Includes:-
        1. company: Company to which this instance belongs to.
        2. questionnaire: The question which is enabled by the company.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company_questionnaires',
    )
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.CASCADE,
        related_name='company_questionnaires',
    )
    currently_active = models.BooleanField(default=True)

    def __str__(self):
        """ Unicode representation of CompanyQuestionnaires Model. """
        return f'{self.company.name} - {self.questionnaire.title}'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["company", "questionnaire"], name="company_questionnaire_unique"
            ),
        )


class QuestionnaireRule(CommonBaseModel):
    """ Model Definition of QuestionnaireRules. 

        This model denotes the rule imposed by the company on a questionnaire.

        Model fields includes:-
        1. company_questionnaire: Foreign key to company and questionnaire relation.
        2. rule: the type of rule imposed by the company.
        3. time: this denotes when questionnaire notification should be sent.
    """

    # Choice mappings for questionnaire rule type.
    RULE_CHOICES = (
        (commons_constant.RULE_DISABLE, 'DISABLE'),
        (commons_constant.RULE_ONBOARDING, 'ONBOARDING'),
        (commons_constant.RULE_ONCE, 'ONCE'),
        (commons_constant.RULE_WEEKLY, 'WEEKLY'),
        (commons_constant.RULE_MONTHLY, 'MONTHLY'),
        (commons_constant.RULE_YEARLY, 'YEARLY'),
        (commons_constant.RULE_DAILY, 'DAILY'),
        (commons_constant.RULE_MANUAL, 'MANUAL'),
    )

    company_questionnaire = models.ForeignKey(
        CompanyQuestionnaire,
        on_delete=models.CASCADE,
        related_name='rule'
    )
    # TODO: these two fields need to be removed
    rule_type = models.IntegerField(
        choices=RULE_CHOICES, default=commons_constant.RULE_DISABLE)
    # last_notified = models.DateTimeField(null=True, blank=True)
    notification = models.OneToOneField(
        PeriodicTask,
        null=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """ Unicode Representation of Questionnaire Rule Model. """
        return f'{self.company_questionnaire.company.name}-{self.company_questionnaire.questionnaire.title}'


class CompanyInvite(CommonBaseModel):
    """ Model Definition for Company Invites. 

        This model will store the details of invites sent by the company
        and their status.

        Model fields includes:-
        1. company: Invite sending company.
        2. receiver: Invite receiving user.
        3. status: boolean to store status of the invite.
    """
    # Constants for Company Invite statuses.
    SENT = 0
    SENT_FAILED = 1
    ACCEPTED = 2
    CANCELLED = 3
    PENDING = 4

    # Choices for Invite statuses.
    COMPANY_INVITE_STATUS_CHOICES = (
        (SENT, 'SENT'),
        (SENT_FAILED, 'SENT_FAILED'),
        (ACCEPTED, 'ACCEPTED'),
        (CANCELLED, 'CANCELLED'),
        (PENDING, 'PENDING')
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company_invites'
    )
    receiver = models.ForeignKey(
        AUTH_USER,
        on_delete=models.CASCADE,
        related_name='company_invites',
    )
    first_name = models.CharField(max_length=commons_constant.MAX_LENGTH)
    last_name = models.CharField(
        max_length=commons_constant.MAX_LENGTH,
        blank=True,
        null=True
    )
    status = models.IntegerField(
        choices=COMPANY_INVITE_STATUS_CHOICES, default=PENDING
    )
    token = models.CharField(max_length=commons_constant.TOKEN_MAX_LENGTH)

    def save(self, *args, **kwargs):
        if not self.id:
            self.token = generate_token()
        super().save()

    def change_invite_status(self, status):
        self.status = status
        self.save(update_fields=['self.status', 'updated_at'])

    def __str__(self):
        """ Unicode representation of CompanyInvite. """
        return f'{self.company.name} invited {self.receiver.get_full_name()}.'

    class Meta:
        ordering = ['-created_at']
