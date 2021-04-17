from django.urls import include, path
from rest_framework.routers import SimpleRouter

from companies import views as companies_view

app_name = 'companies'

router = SimpleRouter()
router.register(
    'company', companies_view.CompanyViewSet, basename='company'
)

router.register(
    '<int:company_id>/company-invite',
    companies_view.ListCompanyInviteViewSet,
    basename='company-invite'
)

router.register(
    '<int:company_id>/employee',
    companies_view.ListCompanyEmployeeViewSet,
    basename='company-employee'
)

router.register(
    'my-companies',
    companies_view.MyCompanyViewSet,
    basename='my-companies'
)

router.register(
    'joined-companies',
    companies_view.JoinedCompanyViewSet,
    basename='joined-companies'
)

# router.register(
#     '<int:company_id>/questionnaire',
#     companies_view.CompanyQuestionnaireViewSet,
#     basename='company-questionnaire'
# )

company_router = SimpleRouter()
company_router.register(
    'questionnaire',
    companies_view.CompanyQuestionnaireViewSet,
    basename='questionnaire'
)

questionaire_rule_router = SimpleRouter()
questionaire_rule_router.register(
    'rule',
    companies_view.QuestionnaireRuleViewSet,
    basename='rule'
)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:company_id>/', include(company_router.urls)),
    path('<int:company_id>/questionnaire/<int:questionnaire_id>/',
         include(questionaire_rule_router.urls)),
    path(
        '<int:company_id>/create-company-invite/',
        companies_view.CompanyInviteAPIView.as_view(),
        name='create-company-invite'
    ),
    path(
        'company-details/<str:token>/',
        companies_view.CompanyDetailsAPIView.as_view(),
        name='company-details'
    ),
    path(
        'accept-company-invite/',
        companies_view.AcceptCompanyInviteAPIView.as_view(),
        name='company-invite-accept'
    ),
    path(
        'cancel-company-invite/',
        companies_view.CancelCompanyInviteAPIView.as_view(),
        name='company-invite-cancel'
    ),
    path(
        'isAdmin/<str:company_id>/',
        companies_view.CheckCompanyAdminAPIView.as_view(),
        name='check-is-admin'
    ),
    path(
        'company-counts/', companies_view.CompanyCountAPIView.as_view(), name='company-count'
    )
]
