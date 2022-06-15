import json
from pydoc import cli
from django.conf import settings
from django.core import mail
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from cloudinary.uploader import upload_image
import django.contrib.auth.views as auth_views


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
                obtainPayload {
                payload {
                    username
                    exp
                    origIat
                }
                token
                refreshExpiresIn
                refreshToken
                }
                errors
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
        print(json.loads(res.content))
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
                obtainPayload {
                payload {
                    username
                    exp
                    origIat
                }
                token
                refreshExpiresIn
                refreshToken
                }
                errors
            }
        }
        """
        verifyToken = """
        mutation {
            verifyToken(token: "%s") {
                success
                errors
                verifyPayload {
                    payload{
                        username
                    }
                }
            }
        }        
        """
        refreshToken = """
        mutation {
            refreshToken(refreshToken: "%s") {
                success
                errors
                refreshPayload {
                    token
                    refreshToken
                    refreshExpiresIn
                    payload {
                        exp
                        origIat
                        username
                    }
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
                    id
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
        r_token = data["obtainPayload"]["refreshToken"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["success"])
        self.assertTrue(
            data["obtainPayload"]["payload"]["username"], self.user.username
        )

        # verify that token
        res = self.client.post(
            self.endpoint,
            data={"query": verifyToken % data["obtainPayload"]["token"]},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["verifyToken"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["success"])
        self.assertEqual(
            data["verifyPayload"]["payload"]["username"], self.user.username
        )

        # refresh that token
        res = self.client.post(
            self.endpoint,
            data={"query": refreshToken % r_token},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["refreshToken"]
        r_token = data["refreshPayload"]["refreshToken"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["success"])

        # TODO ask for me with AUTHORIZATION header
        res = self.client.post(
            self.endpoint,
            data={"query": me},
            content_type="application/json",
            HTTP_AUTHORIZATION="JWT " + data["refreshPayload"]["token"],
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["me"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertIsNotNone(data)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(int(data["profile"]["id"]), self.user.profile.pk)

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
        mutation {
            profileUpdate(
            where: { id: { exact: %s } }
            input: { language: "ar-SA", theme: "dark" }
            ) {
            ok
            errors {
                field
                messages
            }            
            result {
                id
                theme
                language
            }
            }
        }
        """

        # update profile info, with logged out user; causes error
        res = self.client.post(
            self.endpoint,
            data={"query": profileUpdate % self.user.profile.pk},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        errors = json.loads(res.content)["errors"]
        self.assertEqual(
            errors[0]["message"], "You do not have permission to perform this action"
        )
        self.assertEqual(res.wsgi_request.content_type, "application/json")

        # login the user and pass its token in the HTTP header
        self.client.force_login(self.user, settings.AUTHENTICATION_BACKENDS[1])
        # update other user's profile
        res = self.client.post(
            self.endpoint,
            data={"query": profileUpdate % self.user2.profile.pk},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        errors = json.loads(res.content)["errors"]
        self.assertEqual(errors[0]["message"], "You don't own this Profile")

        # update the user profile
        res = self.client.post(
            self.endpoint,
            data={"query": profileUpdate % self.user.profile.pk},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)["data"]["profileUpdate"]
        self.assertEqual(res.wsgi_request.content_type, "application/json")
        self.assertTrue(data["ok"])
        self.assertEqual(data["result"]["language"], "ar-SA")
        self.assertEqual(data["result"]["theme"], "dark")

    def test_profile_pic(self):
        from .test_utils import file_graphql_query

        profilePicUpdate = """      
        mutation File($file: Upload!){
            profilePicUpdate(file: $file){
                success
                profilePic
            }
        }
        """

        # without loging in
        with open("static/img/blank_profile.png", "rb") as file:
            res = file_graphql_query(
                query=profilePicUpdate,
                client=self.client,
                files={"file": file},
                graphql_url=self.endpoint,
            )
        self.assertEqual(res.status_code, 200)
        print(res.content)
        errors = json.loads(res.content)["errors"]
        self.assertEqual(
            errors[0]["message"], "You do not have permission to perform this action"
        )
        self.assertEqual(res.wsgi_request.content_type, "multipart/form-data")

        # loging in the user
        self.client.force_login(self.user, settings.AUTHENTICATION_BACKENDS[1])
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
