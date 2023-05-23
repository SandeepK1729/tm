from django.db import models
from datetime import date

from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.core.mail import send_mail


sex_choice = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    username        = models.CharField(
                        _("Username"),
                        max_length=150,
                        unique=True,
                        help_text=_(
                            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
                        ),
                        validators=[username_validator],
                        error_messages={
                            "unique": _("A user with that username already exists."),
                        },
                    )
    password        = models.CharField(_("password"), max_length=128)
    first_name      = models.CharField(_("first name"), max_length=150, blank=True)
    last_name       = models.CharField(_("last name"), max_length=150, blank=True)
    mobile_number   = models.CharField(
                        blank = False,
                        unique = True, 
                        max_length = 10,
                        help_text = "Enter 10 digit phone number only"
                    )
    email           = models.EmailField(_("email address"), blank=True)
    gender      = models.CharField(
                    max_length=50, 
                    choices=sex_choice, 
                    default='Male'
                )
    dob         = models.DateField(
                    _("date of birth"),
                    default=date.today,
                    null = True,
                    blank = True,
                    help_text="Please use the following format: <em>YYYY-MM-DD</em>."
                )
    date_joined     = models.DateTimeField(_("date joined"), default=timezone.now)
    is_staff        = models.BooleanField(
                        _("staff status"),
                        default = True,
                    )
    is_active       = models.BooleanField(
                        _("active"),
                        default = True,
                    )
    groups          = models.ManyToManyField("group.Group", related_name = "members", blank = True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"

    def get_all_groups(self):
        return self.groups

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class User(AbstractUser):
    # CustomUser model will be act as General class of parent
    pass

