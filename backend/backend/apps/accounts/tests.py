import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from ddf import G
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.utils import TokenGenerator
from commons import constants as commons_constant

AUTH_USER = get_user_model()


def get_user_data(**kwargs):
    """ Method for making dictionary for user model input. """

    data = {
        'email': 'abc@mail.com',
        'first_name': 'first',
        'last_name': 'last',
        'password': 'password132452'
    }

    # Adding fields from kwargs into data.
    data.update(kwargs)

    return data


class UserCreationAPITestCase(APITestCase):

    def setUp(self):
        self.url = reverse('accounts:user-list')

    # Creation Success
    @patch('accounts.serializers.send_account_verification_email_async')
    def test_user_creation_success(self, mock_send_account_verification_email):
        """ Test to check the successful creation of User with valid data. """

        data = get_user_data()

        expected_response_data = data

        response = self.client.post(self.url, data=data)
        
        # Response status.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # User creation inside DB.
        self.assertIsNotNone(
            AUTH_USER.objects.filter(email=data.get('email')).first()
        )

        # Checking if the patched function is called in the API.
        mock_send_account_verification_email.delay.assert_called()

        expected_response_data.update({
            'id': AUTH_USER.objects.get(email=data.get('email')).id,
            'dob': None,
            'phone': None,
            'profile_image': None,
            'is_email_verified': False,
            'token': Token.objects.get(user__id=response.data.get('id')).key,
        })
        del expected_response_data['password']

        # Expected Response.
        self.assertEqual(dict(response.data), expected_response_data)

    def test_required_fields(self):
        """ Test for finding the required fields. 
            Required fields are:
            1. email.
            2. first_name.
            3. password.
        """

        response = self.client.post(self.url, data={})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data.keys()), 3)
        self.assertEqual(
            list(response.data.keys()),
            ['email', 'first_name', 'password']
        )
        self.assertEqual(
            response.data.get('email')[0].__str__(),
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('first_name')[0].__str__(),
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('password')[0].__str__(),
            'This field is required.'
        )

    def test_inputs_with_invalid_data(self):
        """ Test for hitting api with invalid data. """

        # Invalid email and phone
        data = get_user_data(email='abc', phone='9999')

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('email')[0].__str__(),
            'Enter a valid email address.'
        )
        self.assertEqual(
            response.data.get('phone')[0].__str__(),
            "Phone must be entered in the format: '9898989898' and contains exactly 10 digits."
        )

    def test_unique_email(self):
        """ Testcase for unique email id. """

        user1 = G(AUTH_USER, email='same@mail.com')
        user2 = get_user_data(email='same@mail.com')

        response = self.client.post(self.url, data=user2)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('email')[0].__str__(),
            'user with this email already exists.'
        )

    def test_user_updation(self):
        """ Testcase for updation of user.
            This should not update the user's password, email and 
            is_email_verified status.
        """
        user = G(AUTH_USER)

        self.client.force_authenticate(user=user)

        data = get_user_data(is_email_verified=True)

        expected_response = {
            'id': user.id,
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': user.email,
            'dob': user.dob,
            'phone': user.phone,
            'profile_image': f'http://testserver{user.profile_image.url}',
            'is_email_verified': user.is_email_verified,
            'token': user.auth_token.key
        }

        response = self.client.put(f'{self.url}{user.id}/', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(response.data), expected_response)
        self.assertNotEqual(user.password, make_password(data['password']))
        self.assertTrue(not user.is_email_verified)

    def test_user_deletion(self):
        """ Testcase for checking deletion of user. """

        user = G(AUTH_USER)
        self.client.force_authenticate(user=user)

        response = self.client.delete(f'{self.url}{user.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AUTH_USER.objects.filter(id=user.id).count(), 0)
        # As user is soft deleted hence users token will exist.
        self.assertEqual(Token.objects.filter(user__id=user.id).count(), 1)
        self.assertEqual(AUTH_USER.all_objects.filter(id=user.id).count(), 1)

    def test_accessing_other_user_data(self):
        """ Testcase for accessing other user's details. """

        user1 = G(AUTH_USER)
        user2 = G(AUTH_USER)

        self.client.force_authenticate(user=user1)

        # deleting user2 details by user1
        response = self.client.delete(f'{self.url}{user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = get_user_data()
        # updating user2 details by user1
        response = self.client.put(f'{self.url}{user2.id}/', data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_and_list_method_not_allowed(self):
        """ Test for checking retrive method not allowed on the viewset. """
        user = G(AUTH_USER)

        self.client.force_authenticate(user=user)

        # For listing users
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

        # For retrieving request
        response = self.client.get(f'{self.url}{user.id}/')

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_authorised_access(self):
        """ Testcase for authorised access to endpoints. """

        # Updating user info
        response = self.client.put(
            f'{self.url}1/', data={"last_name": "some_name"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data.get('detail'),
            'Authentication credentials were not provided.'
        )

        # Deleting user
        response = self.client.delete(f'{self.url}1/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data.get('detail'),
            'Authentication credentials were not provided.'
        )


class ProfileAPITestCase(APITestCase):
    """ Testcase for viewing Profile of a user. """

    def setUp(self):
        """ Getting the url of the profile api. """
        self.url = reverse('accounts:profile')

    def test_fetching_user_profile(self):
        """ Testcase for fetching user's profile data. """
        user = G(AUTH_USER)

        # Without Authenticating
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data.get('detail'),
            'Authentication credentials were not provided.'
        )

        # After Authenticating.
        self.client.force_authenticate(user=user)

        expected_response = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'dob': user.dob,
            'phone': user.phone,
            'profile_image': 'http://testserver' + user.profile_image.url,
            'is_email_verified': user.is_email_verified,
            'token': user.auth_token.key
        }
        response = self.client.get(f'{self.url}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(response.data), expected_response)


class PasswordUpdateAPITestCase(APITestCase):
    """ Testcase for Password Update API. """

    def setUp(self):
        """ Getting password update api url. """
        self.url = reverse('accounts:update-password')

    def test_updating_password_success(self):
        """ Testcase for updating user's password. """
        user = G(AUTH_USER, password=make_password('old_password'))

        self.client.force_authenticate(user=user)

        data = {
            'old_password': 'old_password',
            'new_password': 'new_password'
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data.get(
                commons_constant.RESPONSE_MSG), commons_constant.PASS_UPDATE_SUCC
        )
        self.assertEquals(
            authenticate(
                email=user.email, password=data.get('new_password')
            ),
            user
        )


class VerifyEmailAPITestCase(APITestCase):
    """ Testcase for EmailVerification API. """

    def get_url(self, token):
        return reverse('accounts:email-verify', kwargs={'token': token})

    def test_verify_valid_token(self):
        """ Testcase to verify the email of the user. """
        user = G(AUTH_USER)

        # checking currentlty is_email_verified is False.
        self.assertEqual(user.is_email_verified, False)

        # Generating token for email verification.
        token = TokenGenerator.generate_token(
            user,
            exp=datetime.datetime.utcnow()
            + datetime.timedelta(
                hours=commons_constant.EMAIL_VERIFICATION_EXPIRATION_TIME_HR
            )
        )

        url = self.get_url(token)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data.get(commons_constant.RESPONSE_TOKEN),
            Token.objects.get(user=user).key
        )
        self.assertEqual(AUTH_USER.objects.get(
            id=user.id).is_email_verified, True)

    def test_verification_with_invalid_token(self):
        """ Testcase to verify the email of the user with invalid token. """
        user = G(AUTH_USER)

        # checking currentlty is_email_verified is False.
        self.assertEqual(user.is_email_verified, False)

        # Generating token for email verification.
        token = TokenGenerator.generate_token(
            user,
            exp=datetime.datetime.utcnow()
            + datetime.timedelta(
                hours=commons_constant.EMAIL_VERIFICATION_EXPIRATION_TIME_HR
            )
        )[:-1]

        url = self.get_url(token)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get(commons_constant.RESPONSE_TOKEN)[0].__str__(),
            commons_constant.INVALID_TOKEN
        )


class ResendVerificationEmailAPITestCase(APITestCase):
    """ Testcase for Resend Verification Email API. """

    def setUp(self):
        self.url = reverse('accounts:resend-email')

    @patch('accounts.serializers.send_account_verification_email_async')
    def test_resend_verification_email_success(self, mock_send_account_verification_email):
        """ Testcase to successfully sending verification email to the user. """
        user = G(AUTH_USER)

        self.client.force_authenticate(user=user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get(commons_constant.RESPONSE_MSG),
            commons_constant.PASS_RESET_LINK_SUCC
        )
        mock_send_account_verification_email.delay.assert_called()

    @patch('accounts.serializers.send_account_verification_email_async')
    def test_resend_verification_email_failure(self, mock_send_account_verification_email):
        """ Testcase to not sending verification email to the already verified user. """
        user = G(AUTH_USER, is_email_verified=True)

        self.client.force_authenticate(user=user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get(commons_constant.RESPONSE_MSG),
            commons_constant.PASS_RESET_LINK_SUCC
        )
        mock_send_account_verification_email.delay.assert_not_called()


class LoginAPITestCase(APITestCase):
    """ Testcases for Login API. """

    def setUp(self):
        self.url = reverse('accounts:login')

    def test_login_success(self):
        """ Testcase for successful logging in. """
        user = G(AUTH_USER, password=make_password('password'))

        login_cred = {
            'email': user.email,
            'password': 'password',
        }

        response = self.client.post(self.url, data=login_cred)

        expected_response = {
            commons_constant.RESPONSE_TOKEN: Token.objects.get(user=user).key
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(response.data), expected_response)

    def test_required_fields(self):
        """ Test for checking the required fields. """

        response = self.client.post(self.url, data={})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data.get('email')[0].__str__(),
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('password')[0].__str__(),
            'This field is required.'
        )

    def test_response_for_invalid_credentials(self):
        """ Test for invalid credentials. """
        user = G(AUTH_USER, password=make_password('right'))

        login_cred = {
            'email': user.email,
            'password': 'wrong',
        }

        response = self.client.post(self.url, data=login_cred)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data.get('non_field_errors')), 1)
        self.assertEqual(
            response.data.get('non_field_errors')[0].__str__(),
            'Invalid Email or Password'
        )


class LogoutAPITestCase(APITestCase):
    """ Testcase for Logout API. """

    def setUp(self):
        self.url = reverse('accounts:logout')

    def test_successful_logout(self):
        """ Testcase for successful logout. """

        user = G(AUTH_USER)

        self.client.force_authenticate(user=user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.filter(user=user).count(), 0)


class ForgetPasswordAPITestCase(APITestCase):
    """ Testcase for Password Forget API. """

    def setUp(self):
        self.url = reverse('accounts:forget')

    @patch('accounts.serializers.send_password_reset_email_async')
    def test_forget_password_success(self, mock_send_password_reset_email_async):
        """ Test for forget password success. """
        user = G(AUTH_USER)

        data = {
            'email': user.email,
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data), 1)
        self.assertEqual(
            response.data.get(commons_constant.RESPONSE_MSG),
            commons_constant.PASS_RESET_LINK_SUCC
        )
        mock_send_password_reset_email_async.delay.assert_called()

    def test_forget_password_with_bad_email(self):
        """ Test for handling forget request with bad email. """

        data = {
            'email': 'abcgmail.com'
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data.get('email')[0].__str__(),
            'Enter a valid email address.'
        )

    def test_forget_password_with_non_existing_email(self):
        """ Test for handling forget request with non existing email. """

        data = {
            'email': 'invalid@email.com',
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data.get('non_field_errors')[0].__str__(),
            "Email Id Doesn't exist."
        )


class ResetPasswordAPITestCase(APITestCase):
    """ Testcase for Password Reset APITestCase. """

    def get_url(self):
        """ Method for returning the reset password url. """
        return reverse('accounts:reset')

    def test_reset_password_successful(self):
        """ Testcase for successfully reseting user's password. """
        user = G(AUTH_USER)

        # Generating token for given user.
        token = TokenGenerator.generate_token(
            user,
            exp=datetime.datetime.utcnow()
            + datetime.timedelta(
                hours=commons_constant.EMAIL_VERIFICATION_EXPIRATION_TIME_HR
            )
        )

        url = self.get_url()

        data = {
            'new_password': 'new_password',
            'token': token
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data.get(commons_constant.RESPONSE_MSG),
            commons_constant.PASS_UPDATE_SUCC
        )

    def test_required_parameters(self):
        """ Testcase for checking required parameter of the API. """

        response = self.client.post(self.get_url(), data={})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data.get('token')[0].__str__(),
            'This field is required.'
        )
        self.assertEqual(
            response.data.get('new_password')[0].__str__(),
            'This field is required.'
        )
