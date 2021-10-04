from django.forms import ModelForm

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Board, Post, Topic
from ..views import PostUpdateView


class PostUpdateViewTestCase(TestCase):
    def setUp(self):
        self.board = Board.objects.create(
            name="Django", description="Django board."
        )
        self.username = "john"
        self.password = "123"
        user = User.objects.create_user(
            username=self.username,
            email="john@doe.com",
            password=self.password,
        )
        self.topic = Topic.objects.create(
            subject="Hello, world", board=self.board, starter=user
        )
        self.post = Post.objects.create(
            message="Lorem ipsum dolor sit amet",
            topic=self.topic,
            created_by=user,
        )
        self.url = reverse(
            "board:edit_post",
            kwargs={
                "pk": self.board.pk,
                "topic_pk": self.topic.pk,
                "post_pk": self.post.pk,
            },
        )


class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase):
    def test_if_only_logged_in_users_can_edit_the_posts(self):
        login_url = reverse("account:login")
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            "{login_url}?next={url}".format(login_url=login_url, url=self.url),
        )


class UnauthorizedPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        username = "jane"
        password = "321"
        User.objects.create_user(
            username=username, email="jane@doe.com", password=password
        )
        self.client.login(username=username, password=password)
        self.response = self.client.get(self.url)

    def test_topic_should_be_edited_only_by_the_owner(self):
        self.assertEquals(self.response.status_code, 404)


class PostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_view_status_code_is_200(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_post_update_view_function(self):
        view = resolve("/boards/1/topics/1/posts/1/edit/")
        self.assertEquals(view.func.view_class, PostUpdateView)

    def test_response_contains_csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_response_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, ModelForm)

    def test_form_inputs(self):
        """
        The view must contain two inputs: csrf, message textarea
        """
        self.assertContains(self.response, "<input", 1)
        self.assertContains(self.response, "<textarea", 1)


class SuccessfulPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(
            self.url, {"message": "edited message"}
        )

    def test_valid_from_submission_should_redirect_the_user(self):
        topic_posts_url = reverse(
            "board:topic_posts",
            kwargs={"pk": self.board.pk, "topic_pk": self.topic.pk},
        )
        self.assertRedirects(self.response, topic_posts_url)

    def test_post_changed(self):
        self.post.refresh_from_db()
        self.assertEquals(self.post.message, "edited message")


class InvalidPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_invalid_form_submmission_should_return_to_the_same_page(self):
        self.assertEquals(self.response.status_code, 200)

    def test_redirected_response_form_contains_form_errors(self):
        form = self.response.context.get("form")
        self.assertTrue(form.errors)
