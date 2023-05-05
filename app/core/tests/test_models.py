"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an username is successful."""
        username = 'testuser'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            username=username,
            password=password,
        )

        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

    def test_new_user_without_username_raises_error(self):
        """Test that creating a user without an username raises a ValueError."""  # noqa: E501
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass123')

    def test_new_user_with_short_password_raises_error(self):
        """Test that creating a user with short password raises a ValueError."""  # noqa: E501
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('testuser', 'test')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'testadmin',
            'test123',
        )

        self.assertTrue(user.is_superuser)
