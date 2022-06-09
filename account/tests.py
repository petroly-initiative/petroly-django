from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from cloudinary.uploader import upload_image


from .models import Profile
from data import departments, years


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
        
        
        # update profile
        origin_img_url = 'https://res.cloudinary.com/petroly-initiative/image/upload/v1622359053/profile_pics/blank_profile.png'
        res = upload_image(
            origin_img_url,
            folder="profile_pics/test/",
            public_id=self.user.username,
            overwrite=True,
            invalidate=True,
            transformation=[{"width": 200, "height": 200, "crop": "fill"}],
            format="jpg",
        )

        self.user.profile.profile_pic = res
        self.user.profile.major = departments[7][0]
        self.user.profile.year = years[2][0]
        self.user.profile.language = 'ar-SA'
        self.user.profile.theme = 'dark'
        self.user.profile.save()

        self.assertEqual(self.user.profile.profile_pic.public_id, f'profile_pics/test/{self.user.username}')
        self.assertEqual(self.user.profile.profile_pic.metadata['original_filename'], 'blank_profile')
        self.assertEqual(self.user.profile.profile_pic.metadata['width'], 200)
        self.assertEqual(self.user.profile.profile_pic.metadata['format'], 'jpg')
        self.assertEqual(self.user.profile.major, departments[7][0])
        self.assertEqual(self.user.profile.year, years[2][0])
        self.assertEqual(self.user.profile.language, 'ar-SA')
        self.assertEqual(self.user.profile.theme, 'dark')


class UserRegisterTestCase(TestCase):

    def setUp(self) -> None:
        super().setUp()

    
