from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from commons import constants as commons_constants
from commons.models import Invite
from commons.permissions import IsEmailVerified
from commons.serializers import InviteCreateSerializer, InviteAcceptSerializer


class InviteCreateAPIView(generics.GenericAPIView):
    """ APIView for Invite Creation. """
    serializer_class = InviteCreateSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def post(self, request, *args, **kwargs):
        """ Method for handling post request. """
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                commons_constants.RESPONSE_MSG: commons_constants.INVITE_SUCC_SENT
            },
            status=status.HTTP_200_OK
        )


class InviteAcceptAPIView(generics.GenericAPIView):
    """ APIView for Invite Accept. """
    serializer_class = InviteAcceptSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """ Method for handling post requests. """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response(
            {
                commons_constants.RESPONSE_MSG: commons_constants.INVITE_ACCEPTED,
                commons_constants.RESPONSE_TOKEN: token
            },
            status=status.HTTP_200_OK
        )
