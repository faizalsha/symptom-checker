from django.urls import include, path

from rest_framework.routers import SimpleRouter

from accounts import views as accounts_views

app_name = 'accounts'

router = SimpleRouter()
router.register('user', accounts_views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', accounts_views.ProfileAPIView.as_view(), name='profile'),
    path(
        'update-password/',
        accounts_views.UpdatePasswordAPIView.as_view(),
        name='update-password'
    ),
    path(
        'resend/',
        accounts_views.ResendVerificationEmailAPIView.as_view(),
        name='resend-email'
    ),
    path(
        'verify/<str:token>/',
        accounts_views.EmailVerifyAPIView.as_view(),
        name='email-verify'
    ),
    path("login/", accounts_views.UserLoginAPIView.as_view(), name="login"),
    path("logout/", accounts_views.UserLogoutAPIView.as_view(), name="logout"),
    path("forget/", accounts_views.ForgetPasswordAPIView.as_view(), name='forget'),
    path("reset/", accounts_views.ResetPasswordAPIView.as_view(), name='reset'),
    path("user-counts/", accounts_views.UserCountAPIView.as_view(), name='user-count'),
]
