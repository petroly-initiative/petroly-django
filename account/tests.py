"""
This module is to test all possible use cases of `account` app.

## Run test
    to run this file only:
    `python manage.py test account/tests.py`

## Coverage:
    - Tests all `account` model operations.
    - Tests all relevant GraphQL API operations.
"""

import json

from django.conf import settings
from django.core import mail
from cloudinary import CloudinaryImage
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
import django.contrib.auth.views as auth_views
from cloudinary.uploader import unsigned_upload
from strawberry_django.test.client import Response
from django.core.exceptions import ObjectDoesNotExist
from gqlauth.jwt.types_ import ObtainJSONWebTokenType
from django.test import TestCase, TransactionTestCase, Client, tag

from data import DepartmentEnum, years
from . import views
from .models import Profile
from .test_utils import file_graphql_query


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
            profile.language,
            Profile._meta.get_field("language").get_default(),
        )
        self.assertEqual(profile.theme, Profile._meta.get_field("theme").get_default())
        self.assertEqual(profile.major, None)
        self.assertEqual(profile.year, None)

    def test_crud_profile(self):
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
        res = unsigned_upload(
            origin_img_url,
            upload_preset="pzgetp4b",
            public_id=self.user.username,
        )

        self.assertEqual(res["public_id"], "profile_pics/test/user-test1")
        self.user.profile.profile_pic = CloudinaryImage(public_id=res["public_id"])
        self.user.profile.major = DepartmentEnum.choices[7][0]
        self.user.profile.year = years[2][0]
        self.user.profile.language = "ar-SA"
        self.user.profile.theme = "dark"
        self.user.profile.save()

        self.assertEqual(
            self.user.profile.profile_pic.public_id,
            f"profile_pics/test/{self.user.username}",
        )
        self.assertEqual(self.user.profile.major, DepartmentEnum.choices[7][0])
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
            res.resolver_match.func.__name__,
            auth_views.LoginView.as_view().__name__,
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
            res.resolver_match.func.__name__,
            views.IndexView.as_view().__name__,
        )

        # logout this user
        res = self.client.post("/account/logout/", follow=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.wsgi_request.path, "/account/logout/")
        self.assertEqual(
            res.resolver_match.func.__name__,
            auth_views.LogoutView.as_view().__name__,
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
            res.resolver_match.func.__name__,
            views.IndexView.as_view().__name__,
        )

        # logout this user
        res = self.client.post("/account/logout/", follow=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.wsgi_request.path, "/account/logout/")
        self.assertEqual(
            res.resolver_match.func.__name__,
            auth_views.LogoutView.as_view().__name__,
        )


class AccountGraphQLTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.endpoint = "/endpoint/"
        cls.client = Client()

        # verified user
        cls.user = get_user_model().objects.create_user(
            username="long-testing",
            password="nothing-is-secret",
            email="i-saw-u@space.com",
        )
        cls.user.status.verified = True
        cls.user.status.save()
        # another user to test reset password
        cls.user2 = get_user_model().objects.create_user(
            username="no-username",
            password="im-done",
            email="siuuu@cccc.com",
        )
        cls.user2.status.verified = True
        cls.user2.status.save()

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
            errors
            }
        }
        """
        tokenAuth = """
        mutation {
            tokenAuth(username: "im-poor-user", password: "%s") {
                success
                errors
                token {
                    token
                    payload {
                        username
                        exp
                        origIat
                    }
                }
                refreshToken {
                    token
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
            self.endpoint,
            data={"query": register},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["register"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["success"])
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

        # dont worry this is the correct pass, but he is not verified yet
        res = self.client.post(
            self.endpoint,
            data={
                "query": tokenAuth % "nothing-is-secret",
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["tokenAuth"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertFalse(data["success"])
        self.assertEqual(data["errors"]["nonFieldErrors"][0]["code"], "not_verified")
        # told ya, he's not verified

        # extract the token from the activation email
        token = ""
        for l in str(mail.outbox[0].message()).split("\n"):
            l = l.strip().removesuffix('"')
            if "petroly.co/confirm/" in l:
                token = l.split("/")[-1]
                break
        # verify the user account
        res = self.client.post(
            self.endpoint,
            data={
                "query": verifyAccount % token,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["verifyAccount"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["success"])

    def test_login(self):
        tokenAuth = """
        mutation {
            tokenAuth(username: "long-testing", password: "nothing-is-secret") {
                success
                errors
                token {
                    token
                    payload {
                        username
                        exp
                        origIat
                    }
                }
                refreshToken{
                    token
                }
            }
        }
        """
        verifyToken = """
        mutation {
            verifyToken(token: "%s") {
                success
                errors
                user {
                    username
                }
            }
        }        
        """
        refreshToken = """
        mutation {
            refreshToken(refreshToken: "%s", revokeRefreshToken:false) {
                success
                errors
                token {
                    token
                    payload {
                        username
                    }
                }
                refreshToken {
                    created
                    revoked
                }
            }
        }
        """
        revokeToken = """
        mutation {
            revokeToken(refreshToken: "%s") {
            success
            errors
            }
        }
        """
        me = """
        query {
            me{
                username
                profile{
                    pk
                    user{
                        username
                    }
                }
            }
        }        
        """

        res = self.client.post(
            self.endpoint,
            data={
                "query": tokenAuth,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["tokenAuth"]
        r_token = data["refreshToken"]["token"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["success"])
        self.assertTrue(data["token"]["payload"]["username"], self.user.username)

        # verify that token
        res = self.client.post(
            self.endpoint,
            data={"query": verifyToken % data["token"]["token"]},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["verifyToken"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["username"], self.user.username)

        # refresh that token
        res = self.client.post(
            self.endpoint,
            data={"query": refreshToken % r_token},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["refreshToken"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["success"])

        # TODO ask for me with AUTHORIZATION header
        res = self.client.post(
            self.endpoint,
            data={"query": me},
            content_type="application/json",
            HTTP_AUTHORIZATION="JWT " + data["token"]["token"],
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["me"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertIsNotNone(data)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(int(data["profile"]["pk"]), self.user.profile.pk)

        # revoke that token
        res = self.client.post(
            self.endpoint,
            data={"query": revokeToken % r_token},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["revokeToken"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["success"])

        # refreshToken should not work now
        res = self.client.post(
            self.endpoint,
            data={"query": refreshToken % r_token},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertFalse(data["refreshToken"]["success"])

    def test_resset_password(self):
        sendPasswordResetEmail = """
        mutation {
            sendPasswordResetEmail(email: "%s") {
                success
            }
        }
        """
        passwordReset = """
        mutation {
            passwordReset(
            token: "%s"
            newPassword1: "new-day-new-strugles"
            newPassword2: "new-day-new-strugles"
            ) {
                success
            }
        }
        """

        # send resset password email
        res = self.client.post(
            self.endpoint,
            data={"query": sendPasswordResetEmail % self.user2.email},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["sendPasswordResetEmail"]["success"])
        self.assertEqual(len(mail.outbox), 1)  # there is an email sent
        self.assertEqual(mail.outbox[0].subject, "Reset your password on petroly.co")
        self.assertIn(self.user2.email, mail.outbox[0].to)

        # extract the token from the resset-password email
        token = ""
        for l in str(mail.outbox[0].message()).split("\n"):
            l = l.strip().removesuffix('"')
            if "petroly.co/password-reset" in l:
                token = l.split("/")[-1]
                break
        # resset password
        res = self.client.post(
            self.endpoint,
            data={"query": passwordReset % token},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["passwordReset"]["success"])

    def test_profile_update(self):
        profileUpdate = """
        mutation Update($pk: ID!, $language: String, $theme: String) {
            profileUpdate(
                data: { 
                    pk: $pk
                    language: $language 
                    theme: $theme
                }
            ) {
                __typename,
                ... on ProfileType {
                    pk
                    language
                    theme
                }
                ... on OperationInfo{
                    messages{
                        kind,
                        message,
                        field
                    }
                }
            }
        }
        """
        tokenAuth = """
        mutation {
            tokenAuth(username: "long-testing", password: "nothing-is-secret") {
                success
                errors
                token {
                    token
                    payload {
                        username
                        exp
                        origIat
                    }
                }
                refreshToken{
                    token
                }
            }
        }
        """

        # update profile info, with logged out user; rasises error
        from strawberry_django.test.client import TestClient

        client = TestClient(self.endpoint)
        res = client.query(
            profileUpdate, {"pk": self.user.profile.pk}, asserts_errors=False
        )
        self.assertIsNone(res.errors)
        self.assertIsNotNone(res.data)
        data = res.data["profileUpdate"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "User is not authenticated.")

        # login the user and pass its token in the HTTP header
        res = client.query(
            tokenAuth,
        )
        assert isinstance(res, Response)
        assert res.data and res.data["tokenAuth"]
        token = res.data["tokenAuth"]["token"]["token"]
        # update other user's profile
        res = client.query(
            profileUpdate,
            variables={
                "pk": self.user2.profile.pk,
                "theme": "dark",
                "language": "ar-SA",
            },
            headers={"AUTHORIZATION": f"JWT {token}"},
        )
        self.assertIsNone(res.errors)
        self.assertIsNotNone(res.data)
        data = res.data["profileUpdate"]
        self.assertEqual(data["messages"][0]["message"], "You don't own this Profile.")

        # update the user profile
        res = client.query(
            profileUpdate,
            {
                "pk": self.user.profile.pk,
                "theme": "dark",
                "language": "ar-SA",
            },
            headers={"AUTHORIZATION": f"JWT {token}"},
        )

        self.assertIsNone(res.errors)
        self.assertIsNotNone(res.data)
        data = res.data["profileUpdate"]
        self.assertEqual(data["language"], "ar-SA")
        self.assertEqual(data["theme"], "dark")

    @tag("require_secretes")
    def test_profile_pic(self):
        profilePicUpdate = """
        mutation File($file: Upload!){
            profilePicUpdate(file: $file){
                success
                profilePic
            }
        }
        """

        # without login in
        with open("static/img/blank_profile.png", "rb") as file:
            res = file_graphql_query(
                query=profilePicUpdate,
                client=self.client,
                files={"file": file},
                graphql_url=self.endpoint,
            )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["profilePicUpdate"]
        self.assertIsNone(data)
        self.assertEqual(res.wsgi_request.content_type, "multipart/form-data")

        # login in the user
        self.client.force_login(self.user, settings.AUTHENTICATION_BACKENDS[0])
        with open("static/img/blank_profile.png", "rb") as file:
            res = file_graphql_query(
                query=profilePicUpdate,
                client=self.client,
                files={"file": file},
                graphql_url=self.endpoint,
            )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["profilePicUpdate"]
        self.assertEqual(res.wsgi_request.content_type, "multipart/form-data")
        self.assertTrue(data["success"])
