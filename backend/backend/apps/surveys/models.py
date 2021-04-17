from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from commons import constants as commons_constant
from commons.models import CommonBaseModel

# Getting the user Model used by Django.
AUTH_USER = settings.AUTH_USER_MODEL


class Question(CommonBaseModel):
    """ Model Definition of Question.

        This model store question information related to some questionnaire.

        Model fields includes:-
        1. text: text field to store question text.
        2. question_type: choice field to store type of the question, MCQ, Binary or text field.
    """

    # Constants for Question Types.
    MCQ = 0
    BINARY = 1
    TEXT = 2

    # Question type choices mapping.
    TYPE_CHOICES = (
        (MCQ, 'MCQ'),
        (BINARY, 'BINARY'),
        (TEXT, 'TEXT'),
    )

    text = models.TextField()
    question_type = models.IntegerField(choices=TYPE_CHOICES, default=MCQ)

    def __str__(self):
        """ Unicode Representation of Question Model. """
        return f'Question-{self.text[:20]}'


class Questionnaire(CommonBaseModel):
    """ Model Definition of Questionnaire.

        This model store information regarding a questionnaire.

        Model fields include:-
        1. title: The title of the questionnaire.
        2. description: The description of the questionnaire describing it.
        3. is_ublished: Boolean field to denote whether this questionnaire is published or not.
        4. published_on: date on which this questionnaire is published.
        5. questions: The questions belonging to this questionnaire.
    """

    title = models.CharField(max_length=commons_constant.MAX_LENGTH)
    description = models.TextField()
    questions = models.ManyToManyField(
        Question, related_name='questionnaire', blank=True
    )
    is_published = models.BooleanField(default=False)
    published_on = models.DateTimeField(null=True, blank=True, editable=False)
    is_mandatory = models.BooleanField(default=False)

    def __str__(self):
        """ Unicode Representation of Questionnaire's Model. """
        return f'{self.title}'


class Choice(CommonBaseModel):
    """ Model definition of Choice.

        This model stores the choices of question.

        Model Field includes:-
        1. question: Question to which this choice belongs to.
        2. text: Choice text.
        3. weightage: the weightage given to some choice.
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
    )
    text = models.TextField()
    # weightage should lie in the range 0 to 100.
    weightage = models.DecimalField(
        default=0.0,
        max_digits=commons_constant.WEIGHTAGE_MAX_DIGITS,
        decimal_places=commons_constant.WEIGHTAGE_DECIMAL_PLACES,
        validators=[MinValueValidator(
            Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )

    def __str__(self):
        """ Unicode representation of Choice Model. """
        return f'{self.text}'


class QuestionnaireResponse(CommonBaseModel):
    """ Model definition of QuestionnaireResponse.

        This model store the information of user's submission to questionnaire for a company.

        Model fields Include:-
        1. user: User who made this submission.
        2. company: Company for which this questionnaire is filled.
        3. questionnaire: Questionnaire which is filled.
    """

    # Constant for risk levels
    LOW = 0
    MEDIUM = 1
    HIGH = 2

    # Choice list for risk level.
    RISK_LEVELS = (
        (LOW, 'LOW'),
        (MEDIUM, 'MEDIUM'),
        (HIGH, 'HIGH'),
    )

    # score ranges for risk levels
    RANGES = {
        'LOW': range(0, 35),
        'MEDIUM': range(36, 67),
        'HIGH': range(68, 100)
    }

    user = models.ForeignKey(
        AUTH_USER,
        on_delete=models.CASCADE,
        related_name='questionnaire_responses'
    )
    # null is set True here, for the case when user fill the questionnaire without
    # company's recommendation.
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='questionnaire_responses',
        null=True,
        blank=True
    )
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.CASCADE,
        related_name='questionnaire_responses'
    )
    score = models.IntegerField(null=True)

    risk_level = models.IntegerField(choices=RISK_LEVELS, default=LOW)

    def __str__(self):
        """ Unicode representation of QuestionnaireResponse Model. """
        return f'{self.questionnaire.title}'

    class Meta:
        ordering = ('-created_at',)


class QuestionResponse(CommonBaseModel):
    """ Model definition of QuestionnaireResponse.

        This model stores the information of the response to a submission.
        1. questionnaire_response: QuestionnaireResponse for which this is response is made.
        2. question: Question for which some response is given.
        3. choice: Choice selected by the user.
        4. user_input:  user's input if the question is of type text field.
    """

    questionnaire_response = models.ForeignKey(
        QuestionnaireResponse,
        related_name='question_responses',
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question,
        related_name='question_responses',
        on_delete=models.CASCADE
    )

    user_input = models.TextField()

    def __str__(self):
        """ Unicode represenatation of QuestionnaireResponse. """
        return f'{self.question.text}'


class Tip(CommonBaseModel):
    """ Model Definition of Tip model.

        This model will store tips provided in the response of result of the questionnaire
        submitted by the user.

        Model Fields Includes:-
        1. questionnaire: Questionnaire to which this tip belongs to.
        2. text: text of the tip.
        3. tip_type: choice field according to the level of risk of the submission.
    """

    # Constant for risk levels
    LOW = 0
    MEDIUM = 1
    HIGH = 2

    # Choice list for risk level.
    RISK_LEVELS = (
        (LOW, 'LOW'),
        (MEDIUM, 'MEDIUM'),
        (HIGH, 'HIGH'),
    )

    questionnaire = models.ForeignKey(
        Questionnaire,
        related_name='tips',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    risk_level = models.IntegerField(choices=RISK_LEVELS, default=LOW)

    def __str__(self):
        """ Unicode respresentation of Tip Model. """
        return f'{self.questionnaire.id} - {self.risk_level}'
