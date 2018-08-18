from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, password, first_name, last_name, role,
                    is_staff, email):
        """
        Creates and saves a User with the given attributes.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=False, last_login=now,
                          date_joined=now, first_name=first_name,
                          last_name=last_name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email):
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, is_staff=True,
                          is_superuser=True, last_login=now, date_joined=now,
                          is_active=True)
        user.set_password(password)
        user.save(using=self.db)
        return user


class User(AbstractBaseUser):
    """
    User that can make modifications on the system
    """

    # User defined roles for 'tasks' module.
    USER_ROLES = (
        ('DIB', 'Dibujante'),
        ('PRO', 'Proyectista'),
        ('ING', 'Ingeniero principal'),
    )

    username = models.CharField(max_length=30, unique=True, blank=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=3, choices=USER_ROLES)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email = models.EmailField()
    date_joined = models.DateTimeField(default=timezone.now)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        if self.username == 'admin':
            full_name = 'admin'
            return full_name

        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
