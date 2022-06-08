import profile
from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.conf import settings
import json

from account.models import Profile



class UserTestCase(TransactionTestCase):
    
    def setUp(self) -> None:
        # create fake user; from project's User model
        self.user_info = {
            'username': 'user-test1',
            'email': 'test1@test.com',
            'password': 'ekrlw32rlwr',
        }
        self.user = get_user_model().objects.create_user( **self.user_info)
        # verify the user: 
        self.user.status.verified = True
        self.user.status.save()


class ProfileTestCase(UserTestCase):
    '''
    Test case for `Profile` model.
    '''

    def setUp(self) -> None:
        # once user is created, a profile is created
        super().setUp()

    def test_auto_create_profile(self):
        # try to get the user's profile
        self.assertTrue(hasattr(self.user, 'profile'))
        profile = Profile.objects.get(user__username=self.user_info['username'])
        self.assertEqual(self.user.profile, profile)

        self.assertEqual(profile.profile_pic.url + '.png', Profile._meta.get_field('profile_pic').get_default())
        self.assertEqual(profile.language, Profile._meta.get_field('language').get_default())
        self.assertEqual(profile.theme, Profile._meta.get_field('theme').get_default())
        self.assertEqual(profile.major, None)
        self.assertEqual(profile.year, None)
        
    def test_crud_prfile(self):
        # Note User:Profile is 1:1 relationship
        # user cannot create profile without a User object
        data = {
            'profile_pic': None,
            'major': None,
            'year': None,
            'language': 'ar-SA',
            'theme': 'dark',
        }

        # create another user
        new_user = get_user_model().objects.create_user(
            username = 'sad-orea',
            email='sdaf@asd.xom',
            password='dsfergvfd',
        )

        # try add another profile to new_user: it should have one already
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user = new_user)

        Profile.objects.filter(user__username='sad-orea').exists()
        self.assertTrue(Profile.objects.filter(user__username='sad-orea').exists())
        profile = Profile.objects.get(user__username='sad-orea')
        
        # delete the user object; will also delete its profile object
        profile.user.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Profile.objects.get(user__username='sad-orea')

        with self.assertRaises(ObjectDoesNotExist):
            get_user_model().objects.get(username='sad-orea')


class UserRegisterTestCase(TestCase):

    def setUp(self) -> None:
        super().setUp()

