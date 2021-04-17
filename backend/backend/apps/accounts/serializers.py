import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from accounts.tasks import send_account_verification_email_async, send_password_reset_email_async
from accounts.utils import TokenGenerator
from commons import constants as commons_constant
from commons.validators import PhoneNumberValidator

AUTH_USER = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """ Serializer class for handling GET, PUT and PATCH requests. """
    token = serializers.SerializerMethodField()

    class Meta:
        model = AUTH_USER
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'dob',
            'phone',
            'profile_image',
            'is_email_verified',
            'token'
        )
        read_only_fields = ('email', 'is_email_verified',)

    def get_token(self, obj):
        """ Method to get user token. """
        return obj.auth_token.key

    def validate_email(self, value):
        """ Validating the input email. """
        return AUTH_USER.objects.normalize_email(value)


class UserPasswordSerializer(UserSerializer):
    """ Serializer class for handing Post requests. """

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('password',)
        read_only_fields = ('is_email_verified',)
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    # def validate_password(self, value):
    #     validate_password(value)
    #     return value

    def create(self, validated_data):
        """ Method for creation of User object with provided validated data. """

        # Creating user instance with validated data.
        user = AUTH_USER.objects.create_user(**validated_data)
        # Generating token for email verification.
        token = TokenGenerator.generate_token(
            user,
            exp=datetime.datetime.utcnow()
            + datetime.timedelta(
                hours=commons_constant.EMAIL_VERIFICATION_EXPIRATION_TIME_HR
            )
        )
        # sending email to the user.
        send_account_verification_email_async.delay(user.email, token)

        return user


class PasswordUpdateSerializer(serializers.Serializer):
    """ Serializer for Password Updation. """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        """ Method to validate old password is valid. """

        user = authenticate(
            email=self.context['request'].user.email,
            password=value
        )

        if user is None:
            raise serializers.ValidationError('Invalid Old Password')

        return value

    def save(self, **kwargs):
        """ Method for updating the user password. """
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """ Serializer for Email Verification. """

    token = serializers.CharField(required=True)

    def validate_token(self, value):
        """ Method for validating the token. """
        decoded_token = TokenGenerator.decode_token(value)

        if decoded_token is None:
            raise serializers.ValidationError(commons_constant.INVALID_TOKEN)

        return decoded_token

    def validate(self, attr):
        """ Method for validating whether the provided token belongs to a user or not. """

        decoded_token = attr['token']

        self.user = AUTH_USER.objects.filter(
            email=decoded_token['email']).first()

        if self.user is None:
            # If there is no user with the provided email id, then raising error.
            raise serializers.ValidationError(commons_constant.INVALID_TOKEN)

        return attr

    def save(self, **kwargs):
        """ Method to update the user.is_email_verified status. """
        self.user.is_email_verified = True
        self.user.save(update_fields=['is_email_verified'])
        return self.user.auth_token.key


class ResendVerificationEmailSerializer(serializers.Serializer):
    """ Serializer for Resending Email Verification."""

    def save(self, **kwargs):
        """ Generating the token for reset password and sending the required email to the user. """

        # If email is already Verified there is no need to send email again.
        # TODO: Keeping the response to be the same as of now.
        if self.context['user'].is_email_verified:
            return

        token = TokenGenerator.generate_token(
            self.context['user'],
            exp=datetime.datetime.utcnow()
            + datetime.timedelta(
                hours=commons_constant.EMAIL_VERIFICATION_EXPIRATION_TIME_HR
            )
        )
        send_account_verification_email_async.delay(
            self.context['user'].email, token
        )
        return token


class UserLoginSerializer(serializers.Serializer):
    """ Serializer for validating and authenticating the input credentials for login. """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        """ Validating the provided email and password are valid or not. """

        self.user = authenticate(
            email=attrs['email'], password=attrs['password'])

        # If User is not authenticated raise validation error.
        if self.user is None:
            raise serializers.ValidationError(f'Invalid Email or Password')

        return attrs

    def save(self, **kwargs):
        """ Method for deleting user's old token and generating a new one. """
        Token.objects.filter(user=self.user).delete()
        Token.objects.create(user=self.user)
        return self.user.auth_token.key


class ForgetPasswordSerializer(serializers.Serializer):
    """ Serializer for ForgetPassword.
        Require to have email as an input.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """ Validating the input email id. """
        return AUTH_USER.objects.normalize_email(value)

    def validate(self, attr):
        """ Validating provided email really belongs to a user or not. """

        self.user = AUTH_USER.objects.filter(email=attr.get('email')).first()

        if self.user is None:
            # If there is no user with the provided email id, then raising error.
            raise serializers.ValidationError("Email Id Doesn't exist.")

        return attr

    def save(self, **kwargs):
        """ Generating the token for reset password and sending the required email to the user. """
        token = TokenGenerator.generate_token(
            self.user,
            exp=datetime.datetime.utcnow()
            + datetime.timedelta(
                hours=commons_constant.EMAIL_VERIFICATION_EXPIRATION_TIME_HR
            )
        )
        send_password_reset_email_async.delay(self.user.email, token)
        return token


class ResetPasswordSerializer(serializers.Serializer):
    """ Serializer for ResetPassword.
        Require to have a token and new_password.
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_token(self, value):
        """ Method for validating the token. """
        decoded_token = TokenGenerator.decode_token(value)

        if decoded_token is None:
            raise serializers.ValidationError(commons_constant.INVALID_TOKEN)

        return decoded_token

    def validate(self, attr):
        """ Method for validating token provided belongs to a user or not. """
        decoded_token = attr['token']

        self.user = AUTH_USER.objects.filter(
            email=decoded_token['email']).first()

        if self.user is None:
            # If there is no user with the provided email id, then raising error.
            raise serializers.ValidationError(commons_constant.INVALID_TOKEN)

        return attr

    def save(self, **kwargs):
        """ Storing the new password for the user. """
        Token.objects.filter(user=self.user).delete()
        self.user.set_password(self.validated_data.get('new_password'))
        self.user.save(update_fields=['password', 'updated_at'])
        Token.objects.create(user=self.user)
        return self.user.auth_token.key


class BasicUserSerializer(serializers.ModelSerializer):
    """ Serializer for showing basic details of user """
    class Meta:
        model = AUTH_USER
        fields = (
            'id',
            'first_name',
            'last_name',
            'email'
        )
        read_only_fields = (
            'id',
            'first_name',
            'last_name',
            'email'
        )
