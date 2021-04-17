import json

from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from accounts.serializers import BasicUserSerializer
from commons import constants as commons_constants
from companies import models as companies_models
from companies import tasks as companies_tasks
from companies.utils import generate_random_string, partially_hide_string

AUTH_USER = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    """ Serializer class for handling `Company` Model """

    class Meta:
        model = companies_models.Company
        fields = (
            'id',
            'name',
            'address',
            'city',
            'state',
            'pincode',
            'registration_date',
            'phone',
            'about',
            'logo',
            'is_verified'
        )
        read_only_fields = (
            'is_verified',
        )

    @transaction.atomic
    def create(self, validated_data):
        """
        Method for creating company and also
        creating employee record in database within a transaction
        """

        company_instance = super().create(validated_data)
        request = self.context['request']
        employee = companies_models.Employee.objects.create(
            user=request.user,
            company=company_instance,
            is_company_admin=True
        )
        return company_instance


class EmployeeSerializer(serializers.ModelSerializer):
    """" Serializer class for `Employee` model """

    user = BasicUserSerializer()

    class Meta:
        model = companies_models.Employee
        fields = [
            'id',
            'user',
            'company',
            'is_company_admin'
        ]


class CompanyInviteSerializer(serializers.Serializer):
    """ Serializer for company invite Model """

    receiver_email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=False)

    @transaction.atomic
    def save(self, **kwargs):
        data = self.data
        request = self.context['request']
        company_id = self.context['view'].kwargs['company_id']
        requesting_user = request.user
        company = companies_models.Company.objects.get(pk=company_id)
        last_name = ''
        if 'last_name' in data:
            last_name = data['last_name']

        is_admin = companies_models.Employee.objects.filter(
            user=requesting_user,
            is_company_admin=True,
            company=company_id
        ).exists()

        if not is_admin:
            raise serializers.ValidationError(
                "You must have admin privilege to perform this action.")

        user_exists = AUTH_USER.objects.filter(
            email=data['receiver_email']).exists()

        if user_exists:
            is_user_already_employee = companies_models.Employee.objects.filter(
                user__email=data['receiver_email'],
                company=company_id
            )
            if is_user_already_employee:
                raise serializers.ValidationError(
                    "User already an employee of this company."
                )

            user = AUTH_USER.objects.get(email=data['receiver_email'])
            last_name = ''
            invite = companies_models.CompanyInvite.objects.create(
                receiver=user,
                company=company,
                first_name=data['first_name'],
                last_name=last_name
            )
            companies_tasks.send_company_invite_email_async.delay(
                data['receiver_email'],
                invite.token
            )
            return f"Company invite has been successfully sent to {invite.receiver.first_name}"
        else:
            password = generate_random_string(
                commons_constants.INTIAL_PASSWORD_LENGHT
            )
            new_user = AUTH_USER.objects.create_user(
                email=data['receiver_email'],
                first_name=data['first_name'],
                last_name=last_name,
                password=password
            )
            invite = companies_models.CompanyInvite.objects.create(
                receiver=new_user,
                company=company,
                first_name=data['first_name'],
                last_name=last_name
            )

            companies_tasks.send_company_invite_email_async.delay(
                data['receiver_email'],
                invite.token,
                password=password
            )
            return f"Company invite has been successfully sent to {invite.receiver.first_name}"


class CompanyInviteActionSerializer(serializers.Serializer):
    """ Base Serializer for accepting or rejecting company invite """

    token = serializers.CharField(required=True)

    def validate(self, attrs):
        token = attrs['token']

        is_token_valid = companies_models.CompanyInvite.objects.filter(
            token=token).exists()

        if not is_token_valid:
            raise serializers.ValidationError('Invalid token')

        invite = companies_models.CompanyInvite.objects.get(token=token)

        is_user_already_employee = companies_models.Employee.objects.filter(
            company=invite.company,
            user=invite.receiver
        )

        if is_user_already_employee:
            raise serializers.ValidationError(
                "User already an employee of this company."
            )

        if invite.receiver != self.context['request'].user:
            partial_email = partially_hide_string(invite.receiver.email)
            raise serializers.ValidationError(
                f'This invite belongs to {partial_email}'
            )

        if invite.status != invite.SENT:
            raise serializers.ValidationError(
                'Token Expired or already used before.'
            )

        return attrs


class CompanyInviteAcceptSerializer(CompanyInviteActionSerializer):
    """ Serializer for accepting company invite """

    @transaction.atomic
    def save(self, **kwargs):
        invite_token = self.data['token']
        invite = companies_models.CompanyInvite.objects.get(token=invite_token)
        invite.change_invite_status(companies_models.CompanyInvite.ACCEPTED)
        companies_models.Employee.objects.create(
            user=invite.receiver,
            company=invite.company
        )
        return f'Successfully joined {invite.company} company'


class CompanyInviteCancelSerializer(CompanyInviteActionSerializer):
    """ Serializer for rejecting company invite """

    def save(self, **kwargs):
        invite_token = self.data['token']
        invite = companies_models.CompanyInvite.objects.get(token=invite_token)
        invite.change_invite_status(companies_models.CompanyInvite.CANCELLED)

        return f'Invite cancelled for {invite.company} company'


class CompanyInviteListSerializer(serializers.ModelSerializer):
    """ Serializer for company invite model """

    email = serializers.SerializerMethodField()

    class Meta:
        model = companies_models.CompanyInvite
        fields = (
            'email',
            'first_name',
            'last_name',
            'status'
        )

    def get_email(self, obj):
        return obj.receiver.email


class CompanyQuestionnaireSerializer(serializers.ModelSerializer):
    """ Serializer for `CompanyQuestionnaire` model """

    class Meta:
        model = companies_models.CompanyQuestionnaire
        fields = ('questionnaire', )

    def validate_questionnaire(self, value):
        """ Validating whether the `questionnaire` already added in company """

        company_id = self.context['view'].kwargs['company_id']

        company_questionnaire = companies_models.CompanyQuestionnaire.objects.filter(
            questionnaire_id=value.id,
            company_id=company_id
        )

        if company_questionnaire.exists():
            raise serializers.ValidationError(
                'Questionnaire already added into company questionnaire'
            )

        return value

    def create(self, validated_data):
        validated_data['company_id'] = self.context['view'].kwargs['company_id']
        return super().create(validated_data)


class CompanyQuestionnaireUpdateSerializer(serializers.ModelSerializer):
    """ Serializer for updating `CompanyQuestionnaire` model """

    class Meta:
        model = companies_models.CompanyQuestionnaire
        fields = ('currently_active', )


class CompanyQuestionnaireDetailsSerializer(serializers.ModelSerializer):
    """ Serializer for retrieve `CompanyQuestionnaire` model """

    questionnaire = serializers.StringRelatedField(many=False)
    company = serializers.StringRelatedField(many=False)

    class Meta:
        model = companies_models.CompanyQuestionnaire
        fields = ('id', 'questionnaire_id', 'questionnaire',
                  'company', 'currently_active')


class CrontabSchedulePeriodicTaskSerializer(serializers.ModelSerializer):
    """ Serializer for `django-celery-beat.models.CrontabSchedule` required for nested serialization """

    class Meta:
        model = CrontabSchedule
        fields = (
            'minute',
            'hour',
            'day_of_week',
            'day_of_month',
            'month_of_year'
        )


class CrontabScheduleSerializer(serializers.ModelSerializer):
    """ Serializer for `django-celery-beat.models.CrontabSchedule` """
    # TODO:  should not be part of comapnies.serializers

    class Meta:
        model = CrontabSchedule
        fields = '__all__'


class CompanyQuestionnaireRuleSerializer(serializers.ModelSerializer):
    """ Serializer for getting `QuestionnaireRule` model."""

    crontab = CrontabSchedulePeriodicTaskSerializer(
        many=False,
        source='notification.crontab'
    )
    enabled = serializers.BooleanField(
        source='notification.enabled'
    )

    class Meta:
        model = companies_models.QuestionnaireRule
        fields = ('id', 'crontab', 'enabled')
        read_only_fields = ('id', 'crontab')
