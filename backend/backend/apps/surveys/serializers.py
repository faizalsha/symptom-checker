from datetime import datetime

from django.db import transaction

from rest_framework import serializers

from commons import constants as commons_constants
from companies import models as companies_models
from surveys import models as surveys_models


class ChoiceSerializer(serializers.ModelSerializer):
    """ Serializer Class for Choice Model. """

    class Meta:
        model = surveys_models.Choice
        fields = (
            "id",
            "text",
        )


class QuestionSerializer(serializers.ModelSerializer):
    """ Serializer Class for Question Model. """

    choices = ChoiceSerializer(many=True)

    class Meta:
        model = surveys_models.Question
        fields = (
            "id",
            "text",
            "question_type",
            "choices",
        )


class QuestionnaireSerializer(serializers.ModelSerializer):
    """ Serializer class for Questionnaire Model. """

    question_counts = serializers.CharField(source="count")

    class Meta:
        model = surveys_models.Questionnaire
        fields = (
            "id",
            "title",
            "description",
            "question_counts",
        )


class QuestionResponseSerializer(serializers.ModelSerializer):
    """ Serializer class for QuestionResponse Model. """

    class Meta:
        model = surveys_models.QuestionResponse
        fields = (
            "id",
            "question",
            "user_input",
        )

    def validate(self, attr):
        """ Validating provided question_responses are valid. """

        question = attr.get("question")
        user_input = attr.get("user_input")

        if question.question_type != surveys_models.Question.TEXT:
            if not question.choices.filter(text=user_input).exists():
                raise serializers.ValidationError(
                    commons_constants.INVALID_USER_INPUT
                )
            else:
                attr['score'] = question.choices.filter(
                    text=user_input
                ).first().weightage

        return attr


class QuestionnaireResponseSerializer(serializers.ModelSerializer):
    """ Serializer class for QuestionnaireResponse Model. """

    question_responses = QuestionResponseSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = surveys_models.QuestionnaireResponse
        fields = (
            "user",
            "company",
            "questionnaire",
            "question_responses",
        )

    def validate(self, attr):
        """ Method to validate if all the questions belong to the same questionnaire. """

        questionnaire = attr.get("questionnaire")
        question_responses = attr.get("question_responses")

        question_in_questionnaire = questionnaire.questions.all()

        if len(question_responses) != question_in_questionnaire.count():
            raise serializers.ValidationError(
                commons_constants.EMPTY_RESPONSE
            )

        for question_response in question_responses:
            question = question_response.get("question")

            if question not in question_in_questionnaire:
                raise serializers.ValidationError(
                    commons_constants.SHOULD_BELONG_TO_SAME_QUESTIONNAIRE
                )

        # Getting the current user from the request.
        attr['user'] = self.context['request'].user
        return attr

    @transaction.atomic
    def create(self, validated_data):
        """ Method to create question response and questionnaire response objects. """

        # Getting out question responses.
        question_responses = validated_data.pop("question_responses")

        # creation of questionnaire response object.
        questionnaire_response = \
            surveys_models.QuestionnaireResponse.objects.create(
                **validated_data
            )

        # Variables for storing risk score for the submission
        mcq_or_binary_questions = 0
        total_weightage = 0

        # List of questions in the response
        questions = []

        for question in question_responses:
            # If question is not of type TEXT we can take get the weightage
            # for the selected option
            if question.get('question').question_type != surveys_models.Question.TEXT:
                mcq_or_binary_questions += 1
                total_weightage += int(question.get('score'))
                question.pop('score')

            questions.append(
                surveys_models.QuestionResponse(
                    **question, questionnaire_response=questionnaire_response
                )
            )

        # creating question responses in bulk.
        surveys_models.QuestionResponse.objects.bulk_create(questions)

        # Calculating risk score of the submission
        if mcq_or_binary_questions != 0:
            questionnaire_response.score = total_weightage//mcq_or_binary_questions
        else:
            questionnaire_response.score = 0

        RISK_RANGES = questionnaire_response.RANGES

        if questionnaire_response.score in RISK_RANGES['MEDIUM']:
            questionnaire_response.risk_level = questionnaire_response.MEDIUM

        if questionnaire_response.score in RISK_RANGES['HIGH']:
            questionnaire_response.risk_level = questionnaire_response.HIGH

        questionnaire_response.save(update_fields=['score', 'risk_level'])

        return questionnaire_response


class TipsSerializer(serializers.ModelSerializer):
    """ Serializer class for Tips. """
    class Meta:
        model = surveys_models.Tip
        fields = (
            'id',
            'text',
            'risk_level',
        )


class PendingQuestionnairesSerializer(serializers.ModelSerializer):
    """ Serializer Class for Pending Company Questionnaires of the user. """

    company_name = serializers.SerializerMethodField()
    questionnaire_title = serializers.CharField(source="questionnaire.title")
    company_name = serializers.CharField(source="company.name")

    class Meta:
        model = companies_models.CompanyQuestionnaire
        fields = (
            'id',
            'company',
            'company_name',
            'questionnaire',
            'questionnaire_title',
        )


class MandatoryQuestionnairesSerializer(serializers.ModelSerializer):
    """ Serializer class for mandatory questionnaires. """
    questionnaire_title = serializers.CharField(source="title")
    questionnaire = serializers.IntegerField(source="id")

    class Meta:
        model = surveys_models.Questionnaire
        fields = (
            'id',
            'questionnaire_title',
            'questionnaire',
        )


class QuestionnaireResponseFetchSerializer(serializers.ModelSerializer):
    """ Serializer class for fetching Questionnaire Responses. """

    company_name = serializers.SerializerMethodField()
    questionnaire_title = serializers.CharField(source="questionnaire.title")
    company_name = serializers.CharField(source="company")

    class Meta:
        model = surveys_models.QuestionnaireResponse
        fields = (
            'id',
            'company',
            'company_name',
            'questionnaire',
            'questionnaire_title',
            'score'
        )


class QuestionResponseFetchSerializer(serializers.ModelSerializer):
    """ Serializer class for Question Response. """
    class Meta:
        model = surveys_models.QuestionResponse
        fields = (
            'id',
            'questionnaire_response',
            'question',
            'user_input',
        )


class QuestionnaireFillRateSerializer(serializers.Serializer):
    """ Serializer class for Questionnaire Fill Rate. """
    date = serializers.DateField(required=True)
    attempted_by = serializers.IntegerField(required=True)
    not_attempted_by = serializers.IntegerField(required=True)


class PotentialEmployeesSerializer(serializers.ModelSerializer):
    """ Serializer class for Punctual Employees who fill questionnaires Earliest. """
    username = serializers.CharField(source="user.get_full_name")

    class Meta:
        model = companies_models.Employee
        fields = (
            'id',
            'user',
            'username',
        )
