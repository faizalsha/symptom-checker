from django.core.validators import RegexValidator

PhoneNumberValidator = RegexValidator(
    regex=r'^\d{10}$',
    message="Phone must be entered in the format: '9898989898' and contains exactly 10 digits."
)
