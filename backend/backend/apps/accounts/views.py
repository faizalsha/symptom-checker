from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts import serializers as accounts_serializers
from accounts.models import User
from accounts.permissions import UserPermission
from accounts.mixins import SerializerMixin
from commons import constants as commons_constant


class UserViewSet(SerializerMixin, viewsets.ModelViewSet):
    """ ViewSet for User Creation, Retrieval, Updation, and Deletion. """

    queryset = User.objects.all()
    permission_classes = [UserPermission]
    http_method_names = ['post', 'put', 'patch', 'delete', ]
    serializer_classes = {
        'POST': accounts_serializers.UserPasswordSerializer,
        'PUT': accounts_serializers.UserSerializer,
        'DELETE': accounts_serializers.UserSerializer,
        'PATCH': accounts_serializers.UserSerializer
    }


class UpdatePasswordAPIView(generics.GenericAPIView):
    """ API View for Updating password of the logged in user. """
    serializer_class = accounts_serializers.PasswordUpdateSerializer

    def post(self, request, *args, **kwargs):
        """ Method for handling Post request to update the user password. """
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                commons_constant.RESPONSE_MSG: commons_constant.PASS_UPDATE_SUCC
            }
        )


class ProfileAPIView(generics.GenericAPIView):
    """ API View for accessing Profile Information of the Logged in User. """
    serializer_class = accounts_serializers.UserSerializer

    def get(self, request, *args, **kwargs):
        """ Method for handling get request for fetching profile data. """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class EmailVerifyAPIView(generics.GenericAPIView):
    """ APIView for EmailVerification of the User. """

    permission_classes = [AllowAny, ]
    serializer_class = accounts_serializers.EmailVerificationSerializer

    def get(self, request, *args, **kwargs):
        """ Method to handle the get request to this view. 
            This method, validates the token received from the user,
            verifies it, and then send back the success status if token is valid.
        """

        serializer = self.get_serializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()

        return Response(
            {commons_constant.RESPONSE_TOKEN: token},
            status=status.HTTP_200_OK
        )


class UserLoginAPIView(generics.GenericAPIView):
    """ View that takes in user credentials and return authentication token. """

    permission_classes = [AllowAny]
    serializer_class = accounts_serializers.UserLoginSerializer

    def post(self, request):
        """ Method for handling Post Request of login. """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response(
            {commons_constant.RESPONSE_TOKEN: token},
            status=status.HTTP_200_OK
        )


class UserLogoutAPIView(views.APIView):
    """ View for logging out the user and deleting its token. """

    def delete(self, request):
        request.user.auth_token.delete()
        return Response({commons_constant.RESPONSE_MSG: commons_constant.LOGOUT})


class BaseForgetPasswordView(generics.GenericAPIView):
    """ Base View Forget Password and ResetPassword. """

    msg = None

    def post(self, request, *args, **kwargs):
        """ Post method for handling request. """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({commons_constant.RESPONSE_MSG: self.msg})


class ForgetPasswordAPIView(BaseForgetPasswordView):
    """ View for handling forget password requests. """
    permission_classes = [AllowAny, ]
    serializer_class = accounts_serializers.ForgetPasswordSerializer
    msg = commons_constant.PASS_RESET_LINK_SUCC


class ResetPasswordAPIView(BaseForgetPasswordView):
    """ View for handling password reset requests. """
    permission_classes = [AllowAny]
    serializer_class = accounts_serializers.ResetPasswordSerializer
    msg = commons_constant.PASS_UPDATE_SUCC


class ResendVerificationEmailAPIView(generics.GenericAPIView):
    """ View for handling forget password requests. """

    serializer_class = accounts_serializers.ResendVerificationEmailSerializer

    def post(self, request, *args, **kwargs):
        """ Get method for handling request. """
        serializer = self.get_serializer(context={'user': request.user})
        serializer.save()
        return Response(
            {
                commons_constant.RESPONSE_MSG: commons_constant.PASS_RESET_LINK_SUCC
            }
        )


class UserCountAPIView(generics.GenericAPIView):
    """ View for counting number of users of the platform. """

    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        """ Method for handling get requests. """
        return Response({
            commons_constant.COUNT: User.objects.count()
        })
