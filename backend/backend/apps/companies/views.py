import json

from django.db.models import F, Q, Subquery, OuterRef, Exists
from django.db import transaction

from rest_framework import viewsets, mixins, generics, status, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django_celery_beat.models import PeriodicTask

from accounts.mixins import SerializerMixin
from commons import constants as commons_constants
from commons.permissions import IsEmailVerified
from companies import models as companies_models
from companies import serializers as companies_serializer
from companies.permissions import IsCompanyAdmin, IsCompanyVerified
from companies import utils as companies_utils

# Create your views here.


class CompanyViewSet(viewsets.ModelViewSet):

    """" ViewSet for company creation, retrieval, updation, and listing """

    # TODO: query set is needed later when we write list and retrieve api
    queryset = companies_models.Company.objects.all()
    serializer_class = companies_serializer.CompanySerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]
    http_method_names = ['post', 'put', 'get']


class MyCompanyViewSet(CompanyViewSet):
    """ ViewSet for getting all the companies where user is admin """

    def get_queryset(self):
        return companies_models.Company.objects.filter(
            Q(
                id__in=Subquery(
                    companies_models.Employee.objects.filter(
                        user__id=self.request.user.id,
                        is_company_admin=True
                    ).values('company__id')
                )
            )
        )


class JoinedCompanyViewSet(CompanyViewSet):
    """ ViewSet for getting companies in which user is an employee """

    def get_queryset(self):
        return companies_models.Company.objects.filter(
            Q(
                id__in=Subquery(
                    companies_models.Employee.objects.filter(
                        user__id=self.request.user.id,
                        is_company_admin=False
                    ).values('company__id')
                )
            )
        )


class CompanyInviteAPIView(generics.GenericAPIView):
    """ APIView for sending company invite """

    serializer_class = companies_serializer.CompanyInviteSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin, IsCompanyVerified]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(
            {commons_constants.RESPONSE_MSG: data},
            status=status.HTTP_201_CREATED
        )


class CompanyInviteActionAPIView(generics.GenericAPIView):
    """ Base class for accepting/rejecting company invite """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(
            {commons_constants.RESPONSE_MSG: data},
            status=status.HTTP_200_OK
        )


class AcceptCompanyInviteAPIView(CompanyInviteActionAPIView):
    """ APIView for accepting company invite """
    serializer_class = companies_serializer.CompanyInviteAcceptSerializer


class CancelCompanyInviteAPIView(CompanyInviteActionAPIView):
    """ GenericAPIView for cancelling company invite """
    serializer_class = companies_serializer.CompanyInviteCancelSerializer


class ListCompanyInviteViewSet(viewsets.ReadOnlyModelViewSet):
    """ ReadOnlyModelViewSet to list or get invite for a company """

    serializer_class = companies_serializer.CompanyInviteListSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def get_queryset(self):
        company = self.kwargs['company_id']
        qs = companies_models.CompanyInvite.objects.filter(
            company=company
        )
        return qs


class ListCompanyEmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """ ReadOnlyModelViewSet to list or get employees in a company """
    serializer_class = companies_serializer.EmployeeSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def get_queryset(self):
        company = self.kwargs['company_id']
        qs = companies_models.Employee.objects.filter(
            company=company
        )
        return qs


class CompanyDetailsAPIView(generics.GenericAPIView):
    """ GenericAPIView for getting company information """

    queryset = companies_models.Company.objects.all()
    serializer_class = companies_serializer.CompanySerializer

    def get(self, request, *args, **kwargs):
        token = self.kwargs['token']

        invite = companies_models.CompanyInvite.objects.filter(
            token=token
        ).first()

        if not invite or invite.status != companies_models.CompanyInvite.SENT:
            return Response(
                {"error": "Invalid Token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if invite.receiver != request.user:
            return Response(
                {
                    "error":
                    f'This invite belongs to {companies_utils.partially_hide_string(invite.receiver.email)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(invite.company)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CheckCompanyAdminAPIView(views.APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def get(self, request, *args, **kwargs):
        return Response(
            {commons_constants.RESPONSE_MSG: True},
            status=status.HTTP_200_OK
        )


class CompanyCountAPIView(generics.GenericAPIView):
    """ API View for getting the counts of the registered Companies. """
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        """ Method for handling get requests. """
        return Response({
            commons_constants.COUNT: companies_models.Company.objects.count()
        })


class CompanyQuestionnaireViewSet(SerializerMixin, viewsets.ModelViewSet):
    """ ViewSet for `CompanyQuestionnaire` model """

    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    http_method_names = ['post', 'put', 'get']
    serializer_classes = {
        'POST': companies_serializer.CompanyQuestionnaireSerializer,
        'PUT': companies_serializer.CompanyQuestionnaireUpdateSerializer,
        'GET': companies_serializer.CompanyQuestionnaireDetailsSerializer,
    }

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return companies_models.CompanyQuestionnaire.objects.filter(
            company__id=company_id
        )

    def create(self, request, *args, **kwargs):
        """ Overriding create() to return customized response message """
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response = Response(
                {commons_constants.RESPONSE_MSG: "Successfully added questionnaire to company"},
                status=status.HTTP_201_CREATED
            )
        return response


class QuestionnaireRuleViewSet(viewsets.ModelViewSet):
    """ ViewSet for `QuestionnaireRule` model """

    permission_classes = [
        IsAuthenticated,
        IsCompanyAdmin
    ]
    serializer_class = companies_serializer.CompanyQuestionnaireRuleSerializer
    http_method_names = ['post', 'get', 'delete', 'put']

    def get_queryset(self):
        """ overriding get_queryset to filter all rules for given company_questionnaire_id """
        return companies_models.QuestionnaireRule.objects.filter(
            company_questionnaire_id=self.kwargs['questionnaire_id']
        ).order_by('-created_at')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """ 
        Overriding create and doing following
        1. Serializing crontab and creating crontab model object
        2. Filtering all company employee's email id (to send email notifications later)
        3. Creating PeriodicTask model object
        """

        company_questionnaire_id = kwargs['questionnaire_id']
        company_id = self.kwargs['company_id']

        # Getting questionnaire id to pass into template link
        questionnaire = companies_models.CompanyQuestionnaire.objects.filter(
            pk=company_questionnaire_id,
            company=company_id
        ).values_list('questionnaire_id', flat=True)

        # If invalid company_questionnaire id is provided in url
        if len(questionnaire) == 0:
            return Response(
                {"detail": "Invalid company questionnaire id"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serializing crontab
        cron_data = request.data.pop('cron', None)
        crontabSerializer = companies_serializer.CrontabScheduleSerializer(
            data=cron_data
        )
        crontabSerializer.is_valid(raise_exception=True)
        crontabSerializer.save()

        # Retrieving company employee's email to pass as the argument in PeriodicTask object
        emails = companies_models.Employee.objects.filter(
            company=company_id
        ).values_list("user__email", flat=True)

        # keyword argument to be passed to PeriodicTask
        task_kwargs = {
            "emails": list(emails),
            "questionnaire_id": questionnaire[0],
            "company_id": company_id
        }

        notification = PeriodicTask.objects.create(
            name=companies_utils.generate_random_string(),
            crontab_id=crontabSerializer.data['id'],
            task='companies.tasks.send_company_questionnaire_notification_async',
            kwargs=json.dumps(task_kwargs),
        )

        company_questionnaire_rule = companies_models.QuestionnaireRule.objects.create(
            notification=notification,
            company_questionnaire_id=company_questionnaire_id
        )
        return Response("Success", status=status.HTTP_201_CREATED)
