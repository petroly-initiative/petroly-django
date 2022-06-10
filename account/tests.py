import json
from django.core import mail
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from cloudinary.uploader import upload_image
import django.contrib.auth.views as auth_views
from pyparsing import line


from .models import Profile
from . import views
from data import departments, years


class UserTestCase(TransactionTestCase):
    def setUp(self) -> None:
        # create fake user; from project's User model
        self.user_info = {
            "username": "user-test1",
            "email": "test1@test.com",
            "password": "ekrlw32rlwr",
        }
        self.user = get_user_model().objects.create_user(**self.user_info)
        # verify the user:
        self.user.status.verified = True
        self.user.status.save()


class ProfileTestCase(UserTestCase):
    """
    Test case for `Profile` model.
    """

    def test_auto_create_profile(self):
        # try to get the user's profile
        self.assertTrue(hasattr(self.user, "profile"))
        profile = Profile.objects.get(user__username=self.user_info["username"])
        self.assertEqual(self.user.profile, profile)

        self.assertEqual(
            profile.profile_pic.url + ".png",
            Profile._meta.get_field("profile_pic").get_default(),
        )
        self.assertEqual(
            profile.language, Profile._meta.get_field("language").get_default()
        )
        self.assertEqual(profile.theme, Profile._meta.get_field("theme").get_default())
        self.assertEqual(profile.major, None)
        self.assertEqual(profile.year, None)

    def test_crud_prfile(self):
        # Note User:Profile is 1:1 relationship
        # user cannot create profile without a User object

        # create another user
        new_user = get_user_model().objects.create_user(
            username="sad-orea",
            email="sdaf@asd.xom",
            password="dsfergvfd",
        )

        # try add another profile to new_user: it should have one already
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=new_user)

        Profile.objects.filter(user__username="sad-orea").exists()
        self.assertTrue(Profile.objects.filter(user__username="sad-orea").exists())
        profile = Profile.objects.get(user__username="sad-orea")

        # delete the user object; will also delete its profile object
        profile.user.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Profile.objects.get(user__username="sad-orea")

        with self.assertRaises(ObjectDoesNotExist):
            get_user_model().objects.get(username="sad-orea")

        # update profile
        origin_img_url = "https://res.cloudinary.com/petroly-initiative/image/upload/v1622359053/profile_pics/blank_profile.png"
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
        self.user.profile.language = "ar-SA"
        self.user.profile.theme = "dark"
        self.user.profile.save()

        self.assertEqual(
            self.user.profile.profile_pic.public_id,
            f"profile_pics/test/{self.user.username}",
        )
        self.assertEqual(
            self.user.profile.profile_pic.metadata["original_filename"], "blank_profile"
        )
        self.assertEqual(self.user.profile.profile_pic.metadata["width"], 200)
        self.assertEqual(self.user.profile.profile_pic.metadata["format"], "jpg")
        self.assertEqual(self.user.profile.major, departments[7][0])
        self.assertEqual(self.user.profile.year, years[2][0])
        self.assertEqual(self.user.profile.language, "ar-SA")
        self.assertEqual(self.user.profile.theme, "dark")


class AccountViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        # create fake user
        cls.user = get_user_model().objects.create_user(
            username="freshman",
            email="sadness@kfupm.com",
            password="stay-strong",
        )
        cls.admin = get_user_model().objects.create_user(
            username="senior",
            email="happieness@kfupm.com",
            password="stay-whatsoever",
            is_staff=True,
        )

    def test_forbidden_user(self):
        # non admin user cannot open any page
        # except the login page
        res = self.client.get("/account/login/", follow=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.wsgi_request.path, "/account/login/")
        self.assertTemplateUsed(res, "registration/login.html")
        self.assertEqual(
            res.resolver_match.func.__name__, auth_views.LoginView.as_view().__name__
        )

        # login with wrong credientials user
        res = self.client.post(
            "/account/login/",
            follow=True,
            data={"username": "blah", "password": "im tired writing tests"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "registration/login.html")

        # login a non-staff user
        res = self.client.post(
            "/account/login/",
            follow=True,
            data={"username": "freshman", "password": "stay-strong"},
        )
        self.assertEqual(res.status_code, 403)  # not allowed
        self.assertEqual(res.wsgi_request.path, "/account/")
        self.assertEqual(
            res.resolver_match.func.__name__, views.IndexView.as_view().__name__
        )

        # logout this user
        res = self.client.post("/account/logout/", follow=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.wsgi_request.path, "/account/logout/")
        self.assertEqual(
            res.resolver_match.func.__name__, auth_views.LogoutView.as_view().__name__
        )

    def test_staff_user(self):
        # login a staff user
        res = self.client.post(
            "/account/login/",
            follow=True,
            data={"username": "senior", "password": "stay-whatsoever"},
        )

        self.assertEqual(res.status_code, 200)  # allowed
        self.assertEqual(res.wsgi_request.path, "/account/")
        self.assertEqual(
            res.resolver_match.func.__name__, views.IndexView.as_view().__name__
        )

        # logout this user
        res = self.client.post("/account/logout/", follow=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.wsgi_request.path, "/account/logout/")
        self.assertEqual(
            res.resolver_match.func.__name__, auth_views.LogoutView.as_view().__name__
        )


class AccountGraphQLTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.endpoint = "/endpoint/"
        cls.client = Client()

        cls.user = get_user_model().objects.create_user(
            username="long-testing",
            password="nothing-is-secret",
            email="i-saw-u@space.com",
        )

    def test_user_cycle(self):
        register = """
        mutation {
            register(
            email: "i-saw-u@somewhere.com"
            username: "im-poor-user"
            password1: "nothing-is-secret"
            password2: "nothing-is-secret"
            ) {
            success
            token
            refreshToken
            }
        }
        """
        tokenAuth = """
        mutation {
            tokenAuth(username: "im-poor-user", password: "%s") {
                success
                token
                refreshToken
                user {
                    username
                    verified
                }
            }
        }
        """
        verifyAccount = """
        mutation {
            verifyAccount(token: "%s") {
            success
            }
        }
        """

        res = self.client.post(
            self.endpoint, data={"query": register}, content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["register"]["success"])
        self.assertEqual(len(mail.outbox), 1)  # there is an email sent
        self.assertEqual(mail.outbox[0].subject, "Activate your account on petroly.co")
        self.assertIn("i-saw-u@somewhere.com", mail.outbox[0].to)

        # the user is not verified yet. check that
        # first try wrong password
        res = self.client.post(
            self.endpoint,
            data={
                "query": tokenAuth % "dude-wrong",
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertFalse(data["tokenAuth"]["success"])

        # dont worry this is the correct pass
        res = self.client.post(
            self.endpoint,
            data={
                "query": tokenAuth % "nothing-is-secret",
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["tokenAuth"]["success"])
        self.assertFalse(data["tokenAuth"]["user"]["verified"])
        # told ya, he's not verified

        # extract the token from the activation email
        token = ""
        for l in str(mail.outbox[0].message()).split("\n"):
            l = l.strip().removesuffix('"')
            if "petroly.co/confirm/" in l:
                token = l.split("/")[-1]
                break
        # verify the user
        res = self.client.post(
            self.endpoint,
            data={
                "query": verifyAccount % token,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["verifyAccount"]["success"])
        

    def test_login(self):
        verifyToken = """
        mutation {
            verifyToken(token: "%s") {
            success
            errors
            payload
            }
        }        
        """
        refreshToken = """
        mutation {
            refreshToken(refreshToken: "%s") {
            success
            errors
            refreshToken
            token
            payload
            }
        }
        """
        revokeToken = """
        mutation {
            revokeToken(refreshToken: "%s") {
            success
            errors
            revoked
            }
        }
        """

        # verify that token
        res = self.client.post(
            self.endpoint,
            data={"query": verifyToken % data["register"]["token"]},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["verifyToken"]["success"])

        # refresh that token
        res = self.client.post(
            self.endpoint,
            data={"query": refreshToken % r_token},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        r_token = data["refreshToken"]["refreshToken"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["refreshToken"]["success"])

        # refresh that token
        res = self.client.post(
            self.endpoint,
            data={"query": revokeToken % r_token},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["revokeToken"]["success"])

    def test_resset_password(self):
        # TODO send password email request
        # TODO set new pass
        pass

    def test_profile_update(self):
        ...
