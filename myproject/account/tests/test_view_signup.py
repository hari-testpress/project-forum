from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

from ..views import signup
from ..forms import SignUpForm


class SignUpTests(TestCase):
    def setUp(self):
        url = reverse("account:signup")
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve("account/signup/")
        self.assertEquals(view.func, signup)

    def test_form_contains_csrf_token_field(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_response_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, SignUpForm)

    def test_signup_form_contains_five_inputs(self):
        self.assertContains(self.response, "<input", 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)


class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse("account:signup")
        data = {
            "username": "hari",
            "email": "hari@testpress.in",
            "password1": "abcdef123456",
            "password2": "abcdef123456",
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse("index")

    def test_valid_form_submission_should_redirect_the_user_to_the_home_page(
        self,
    ):
        self.assertRedirects(self.response, self.home_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_is_authenticated_after_successful_signup(self):
        response = self.client.get(self.home_url)
        user = response.context.get("user")
        self.assertTrue(user.is_authenticated)


class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = reverse("signup")
        self.response = self.client.post(url, {})  # submit an empty dictionary

    def test_invalid_form_submission_should_return_to_the_same_page(self):
        self.assertEquals(self.response.status_code, 200)

    def test_form_contains_errors_for_invalid_inputs_after_the_invalid_submission(
        self,
    ):
        form = self.response.context.get("form")
        self.assertTrue(form.errors)

    def test_invalid_signup_dont_create_user(self):
        self.assertFalse(User.objects.exists())
