from django.urls import path, include

from rest_framework.routers import SimpleRouter

from surveys import views as surveys_views

router = SimpleRouter()
router.register(
    'questionnaire', surveys_views.QuestionnaireViewSet, basename='questionnaire'
)
router.register(
    'questions', surveys_views.QuestionViewSet, basename='questions'
)
router.register(
    'pending', surveys_views.PendingQuesitonnairesViewSet, basename='pending'
)
router.register(
    'submission', surveys_views.QuestionnaireResponseViewSet, basename='submission'
)
router.register(
    'question-responses', surveys_views.QuestionResponseViewSet, basename='question-responses'
)
router.register(
    'mandatory', surveys_views.MandatoryQuestionnairesViewSet, basename='mandatory'
)
available_questionaire_router = SimpleRouter()
available_questionaire_router.register(
    'available-questionnaire',
    surveys_views.AvailableQuestionnaireForCompanyViewSet,
    basename='available-questionnaire'
)

app_name = 'surveys'

urlpatterns = [
    path('', include(router.urls)),
    path('<int:company_id>/', include(available_questionaire_router.urls)),
    path('submit/', surveys_views.QuestionnaireSubmissionAPIView.as_view(), name='submit'),
    path(
        'tips/<int:responseId>/', surveys_views.TipsAPIVIew.as_view(), name='questionnaire-tips'
    ),
    path(
        'company/<int:pk>/fill-rate/<int:qid>/',
        surveys_views.QuestionnaireFillRateAPIView.as_view(), name='fill-rate'
    ),
    # path(
    #     'company/<int:pk>/punctual/',
    #     surveys_views.PunctualEmployeesAPIView.as_view(), name='punctual'
    # ),
    path(
        'company/<int:pk>/corona/',
        surveys_views.CoronaProneEmployeesAPIView.as_view(), name='corona'
    ),
    path(
        'company/<int:pk>/depress/',
        surveys_views.DepressionProneEmployeesAPIView.as_view(), name='depress'
    ),
    path(
        'survey-counts/', surveys_views.SurveyCountAPIView.as_view(), name='survey-counts'
    ),
]
