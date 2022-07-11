"""
This module is to test all possible use cases of the `account` app.

## Run tests
    to run these tests only excute:
    `python manage.py test account.tests

## Coverage:
    - It tests the models' operations.
    - It tests all written GraphQL queries and mutations.
"""


from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTestCase(TestCase):
    """
    To set up a test user
    """

    def setUp(self) -> None:
        """Set up a user"""
        self.user_info = {
            "username": "user-with-no-brain",
            "email": "this-isnot-mine@you.me",
            "password": "its-secret",
        }
        self.user: User = get_user_model().objects.create_user(**self.user_info)
        # make it verified
        self.user.status.verified = True
        self.user.status.save()


class InstructorTestCase(UserTestCase):
    """
    To test the `Instructor` model
    """

    def test_create_instructor(self) -> None:
        """Test create an instance of `Instructor`"""
        self.assertIsNotNone(self.user)
