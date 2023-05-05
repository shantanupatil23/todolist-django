"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, username, password, **extra_fields):
        """"Create, save and return a new user."""
        # raise ValueError('force raise ValueError.')
        if not username:
            raise ValueError('User must have an username.')
        if len(password) < 6:
            raise ValueError('Password must be at least 6 char long.')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    username = models.CharField(max_length=255, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
