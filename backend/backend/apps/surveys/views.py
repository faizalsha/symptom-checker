from django.db.models import F, Q, Subquery, OuterRef, Exists, Count, Sum, IntegerField, Avg
from django.db.models.functions import TruncDate

from rest_framework import viewsets, generics, mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from commons import constants as commons_constant
from commons.permissions import IsEmailVerified
from companies import models as companies_models
from surveys import serializers as surveys_serializers
from surveys import models as surveys_models
from surveys.filters import QuestionResponseFilters, QuestionFilters
from companies.permissions import IsCompanyAdmin


class QuestionnaireViewSet(viewsets.ReadOnlyModelViewSet):
    """ Viewset for readonly operations on Questionnaire. """
    permission_classes = [IsAuthenticated, IsEmailVerified]
    serializer_class = surveys_serializers.QuestionnaireSerializer
    queryset = surveys_models.Questionnaire.objects.filter(
        is_published=True
    ).annotate(count=Count('questions'))


class AvailableQuestionnaireForCompanyViewSet(QuestionnaireViewSet):
    """ 
    Viewset for readonly operation for those questionnaire which are not 
    included in company questionnaire
    """
    permission_classes = [IsAuthenticated, IsEmailVerified, IsCompanyAdmin]

    def get_queryset(self):
        return surveys_models.Questionnaire.objects.exclude(
            company_questionnaires__company=self.kwargs['company_id']
        ).annotate(count=Count('questions')).order_by('-created_at')


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """ Viewset for readonly operations on Questions. """
    permission_classes = [IsAuthenticated, IsEmailVerified]
    serializer_class = surveys_serializers.QuestionSerializer
    queryset = surveys_models.Question.objects.all()
    filterset_class = QuestionFilters


class QuestionnaireSubmissionAPIView(generics.GenericAPIView):
    """ API View for submitting questionnaire response. """
    serializer_class = surveys_serializers.QuestionnaireResponseSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        questionnaire_response = serializer.save()
        return Response(
            {
                'id': questionnaire_response.id,
                commons_constant.RESPONSE_MSG: commons_constant.SUBMISSION_SUCC,
                commons_constant.RISK_SCORE: questionnaire_response.score
            },
            status=status.HTTP_201_CREATED
        )


class TipsAPIVIew(generics.ListAPIView):
    """ API View for getting tips for a given response. """
    serializer_class = surveys_serializers.TipsSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        """ method of getting tips for a response belonging to requesting user."""
        responseId = self.kwargs['responseId']
        return surveys_models.Tip.objects.filter(
            questionnaire__questionnaire_responses__user__id=self.request.user.id,
            questionnaire__questionnaire_responses__id=responseId,
            risk_level=F('questionnaire__questionnaire_responses__risk_level')
        )


class PendingQuesitonnairesViewSet(viewsets.ReadOnlyModelViewSet):
    """ Viewset for pending questionnaires of a user required to be filled. """

    serializer_class = surveys_serializers.PendingQuestionnairesSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_queryset(self):

        # filter out company questionnaires, in which the user is involved.
        qs = companies_models.CompanyQuestionnaire.objects.filter(
            company__id__in=Subquery(
                companies_models.Employee.objects.filter(
                    user__id=self.request.user.id
                ).values('company__id')
            )
        )

        # annotate to find whether current questionnaire response is attempted or not.
        qs = qs.annotate(
            attempted=Exists(
                surveys_models.QuestionnaireResponse.objects.filter(
                    user__id=self.request.user.id,
                    company__id=OuterRef('company__id'),
                    questionnaire__id=OuterRef('questionnaire__id'),
                    created_at__gte=OuterRef('rule__last_notified')
                )
            )
        )

        # filter out the non attempted only company questionnaire.
        qs = qs.filter(attempted=False)
        return qs


class MandatoryQuestionnairesViewSet(viewsets.ReadOnlyModelViewSet):
    """ Viewset for mandatory questionnaires. """
    serializer_class = surveys_serializers.MandatoryQuestionnairesSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        """ Method for returning the queryset required for this viewset. """
        qs = surveys_models.Questionnaire.objects.filter(
            is_published=True, is_mandatory=True
        )
        qs = qs.annotate(
            attempted=Exists(
                surveys_models.QuestionnaireResponse.objects.filter(
                    user__id=self.request.user.id,
                    questionnaire__id=OuterRef('id'),
                    company=None
                )
            )
        )
        return qs.filter(attempted=False)


class QuestionnaireResponseViewSet(viewsets.ReadOnlyModelViewSet):
    """ ViewSet for Retrieving Questionnaire Response. """

    serializer_class = surveys_serializers.QuestionnaireResponseFetchSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        return surveys_models.QuestionnaireResponse.objects.filter(user=self.request.user)


class QuestionResponseViewSet(viewsets.ReadOnlyModelViewSet):
    """ API View for fetching question responses of a questionnaire response. """
    serializer_class = surveys_serializers.QuestionResponseFetchSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]
    filterset_class = QuestionResponseFilters

    def get_queryset(self):
        return surveys_models.QuestionResponse.objects.filter(
            questionnaire_response__user=self.request.user
        )


class QuestionnaireFillRateAPIView(generics.ListAPIView):
    """ API View for Questionnaire Fill Rate of a company for a questionnaire. """
    serializer_class = surveys_serializers.QuestionnaireFillRateSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        """ Method for getting the queryset for the view. """
        # Getting pk of company and questionnaire id from the parameters.
        pk = self.kwargs['pk']
        qid = self.kwargs['qid']

        # Filter out the questionnaireResponses belonging to given company and questionnaire.
        qs = surveys_models.QuestionnaireResponse.objects.filter(
            company__id=pk, questionnaire__id=qid
        )
        # Annotating to get date out of the datetime field and Grouping by Data.
        qs = qs.annotate(date=TruncDate('created_at')).values('date')
        # Annotating to get count of entries having same date and ordering by date in Increasing order.
        qs = qs.annotate(attempted_by=Count('id')).order_by('date')
        # Annotating to get the count of employees who have'nt attempted.
        qs = qs.annotate(
            not_attempted_by=Subquery(
                companies_models.Employee.objects.filter(
                    company__id=pk, created_at__date__lte=OuterRef('date')
                ).values('company').annotate(count=Count('company')).values('count'),
                output_field=IntegerField()
            ) - F('attempted_by')
        )
        return qs


# class PunctualEmployeesAPIView(generics.ListAPIView):
#     """ API View for punctual employees. """
#     serializer_class = surveys_serializers.PotentialEmployeesSerializer
#     permission_classes = [IsAuthenticated, IsEmailVerified]

#     def get_queryset(self):
#         pk = self.kwargs['pk']
#         qs = companies_models.Employee.objects.filter(company__id=pk)
#         qs = qs.annotate(delay=Avg())
#         qs = qs.order_by('delay')
#         return qs


# corona prone employees
class CoronaProneEmployeesAPIView(generics.ListAPIView):
    """  API View for listing top 5 employees they may have Corona."""
    serializer_class = surveys_serializers.PotentialEmployeesSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        pk = self.kwargs['pk']
        qs = companies_models.Employee.objects.filter(company__id=pk)
        qs = qs.annotate(
            risk_score=Subquery(
                surveys_models.QuestionnaireResponse.objects.filter(
                    user__id=OuterRef('user__id'),
                    questionnaire__title__iexact='corona',
                    company__id=OuterRef('company__id')
                ).order_by().values('company').annotate(avg=Avg('score')).values('avg'),
                output_field=IntegerField()
            )
        )
        qs = qs.filter(~Q(risk_score=None)).order_by('-risk_score')[:5]

        return qs


class DepressionProneEmployeesAPIView(generics.ListAPIView):
    """ API View for Depression prone employees. """
    serializer_class = surveys_serializers.PotentialEmployeesSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        pk = self.kwargs['pk']
        qs = companies_models.Employee.objects.filter(company__id=pk)
        qs = qs.annotate(
            risk_score=Subquery(
                surveys_models.QuestionnaireResponse.objects.filter(
                    user__id=OuterRef('user__id'),
                    questionnaire__title__iexact='mental health',
                    company__id=OuterRef('company__id')
                ).order_by().values('company').annotate(avg=Avg('score')).values('avg'),
                output_field=IntegerField()
            )
        )
        qs = qs.filter(~Q(risk_score=None)).order_by('-risk_score')[:5]

        return qs


class SurveyCountAPIView(generics.GenericAPIView):
    """ API View for number of surveys present on the platform. """
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        """ Method for handling get requests. """
        return Response({
            commons_constant.COUNT: surveys_models.Questionnaire.objects.count()
        })
