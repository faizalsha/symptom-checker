from django.urls import path

from commons.views import InviteCreateAPIView, InviteAcceptAPIView

app_name = 'commons'

urlpatterns = [
    path('invite/', InviteCreateAPIView.as_view(), name='send-invite'),
    path('accept/', InviteAcceptAPIView.as_view(), name='accept-invite'),
]