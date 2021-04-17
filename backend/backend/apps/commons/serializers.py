from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from commons import constants as commons_constants
from commons import models as commons_models

AUTH_USER = get_user_model()


class InviteCreateSerializer(serializers.ModelSerializer):
    """ Serializer for User Invite to join the platform. """

    class Meta:
        model = AUTH_USER
        fields = (
            'email',
            'first_name',
            'last_name',
        )

    def validate_email(self, value):
        """ Method to validate email id. """
        return AUTH_USER.objects.normalize_email(value)

    @transaction.atomic
    def create(self, validated_data):
        """ Method for creating the Invite. """

        receiver = AUTH_USER.objects.create(**validated_data)
        sender = self.context['request'].user

        invite_instance = commons_models.Invite.objects.create(
            sender=sender, receiver=receiver
        )
        return invite_instance


class InviteAcceptSerializer(serializers.Serializer):
    """ Serializer class for Accepting Invite. """
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_token(self, token):
        """ Method for validating token. """
        self.instance = commons_models.Invite.objects.filter(
            invite_token=token
        ).first()

        if self.instance is None:
            # If token is tempered or some random token then raise exception.
            raise serializers.ValidationError(commons_constants.INVALID_TOKEN)
        if self.instance.invite_status != commons_models.Invite.SENT:
            # If token is already used in the past, then raise exception.
            raise serializers.ValidationError(commons_constants.TOKEN_EXPIRED)
        return token

    @transaction.atomic
    def save(self, **kwargs):
        """ Method for updating user's password, is_email_verified and invite status. """

        password = self.validated_data['password']
        user = self.instance.receiver

        user.set_password(password)
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified','password', 'updated_at'])

        self.instance.invite_status = commons_models.Invite.ACCEPTED
        self.instance.save(update_fields=['invite_status', 'updated_at'])
        return user.auth_token.key
