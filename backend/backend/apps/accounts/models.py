from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserSoftManager, UserHardManager
from commons import constants as commons_constant
from commons.models import CommonBaseModel
from commons.validators import PhoneNumberValidator


class User(AbstractUser, CommonBaseModel):
    """ Model Definition of User Model. 

        Email, first_name are required fields, others are optional.
    """

    # Setting non required fields of the Abstract User to None.
    username = None
    username_validator = None
    date_joined = None

    # Making email of the user, unique field.
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=commons_constant.MAX_LENGTH)

    # Field for storing Users Phone number of length 10 only.
    # Phone number should contain exact 10 Digits only.
    phone = models.CharField(
        max_length=commons_constant.PHONE_NUMBER_LENGTH,
        validators=[PhoneNumberValidator],
        null=True,
        blank=True
    )

    # Field for storing Date of Birth.
    dob = models.DateField(null=True, blank=True)

    # Field for storing profile Image.
    profile_image = models.ImageField(upload_to="user_profile", blank=True)

    # Boolean field for checking is Email Id of the user is verified or not.
    is_email_verified = models.BooleanField(default=False)

    # Manager for accessing objects same as normal Manager(models.Manager).
    all_objects = UserHardManager()
    # Manager for Solt deletion operation.
    objects = UserSoftManager()

    # Marking email as the UserName Field
    USERNAME_FIELD = 'email'

    # Making first_name a required field.
    REQUIRED_FIELDS = ('first_name',)

    def __str__(self):
        """ Unicode Representation of User model. """

        return f'{self.get_full_name()}'
