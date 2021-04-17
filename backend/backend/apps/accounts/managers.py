from django.contrib.auth.models import BaseUserManager

from commons.models import SoftDeleteManager, PermanentDeleteManager


class UserManager(BaseUserManager):
    """ Manager class for Customised User. 

        This inherits from :-
        SoftDeleteManager - This will allow soft delete operation.
        BaseUserManager - This will give access to methods defined
        for normalising email, making hash of password etc.
    """

    def _create_user(self, email, first_name, password, **extra_fields):
        """
        Private method to check for USERNAME FIELD and REQUIRED FIELDS.
        Creates and returns Instance of User.
        """

        # USERNAME FIELD
        if not email:
            raise ValueError("The given email must be set")

        # REQUIRED FIELD
        if not first_name:
            raise ValueError("The given first name must be set")

        # Normalising the User's entered Email.
        email = self.normalize_email(email)

        # Creating an instance of User Model with the provided data.
        user = self.model(email=email, first_name=first_name, **extra_fields)

        # Setting the user's provided password after hashing it.
        user.set_password(password)

        # Saving user's instance into the database, which is provided as default
        # in the setting.py
        user.save(using=self._db)

        return user

    def create_user(self, email, first_name, password, **extra_fields):
        """ Overriding create user method which creates a normal user. """

        # Setting default values of is_staff and is_superuser to be False.
        # Is these keys already given this default value get ignored.
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, first_name, password, **extra_fields)

    def create_superuser(self, email, first_name, password, **extra_fields):
        """ Overriding create super user method which creates a superuser """

        # Setting default values of is_staff and is_superuser to be False.
        # Is these keys already given this default value get ignored.
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_email_verified", True)

        # Checking values of is_staff and is_superuser, which should be true
        # for creating a superuser
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True.')

        return self._create_user(email, first_name, password, **extra_fields)


class UserSoftManager(SoftDeleteManager, UserManager):
    """ Manager for handling SoftDeletion on User Model. """
    pass


class UserHardManager(PermanentDeleteManager, UserManager):
    """ Manager for handling HardDeletion on User Model. """
    pass
