from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..forms import PostForm
from ..models import Board, Post, Topic
from ..views import reply_topic


class ReplyTopicTestCase(TestCase):
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
        Post.objects.create(
            message="Lorem ipsum dolor sit amet",
            topic=self.topic,
            created_by=user,
        )
        self.url = reverse(
            "board:reply_topic",
            kwargs={"pk": self.board.pk, "topic_pk": self.topic.pk},
        )


class LoginRequiredReplyTopicTests(ReplyTopicTestCase):
    def test_should_redirect_anonymous_user_to_the_login_page(self):
        login_url = reverse("account:login")
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            "{login_url}?next={url}".format(login_url=login_url, url=self.url),
        )


class ReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code_is_200(self):
        self.assertEquals(self.response.status_code, 200)

    def test_reply_topic_url_resolves_view_function(self):
        view = resolve("/boards/1/topics/1/reply/")
        self.assertEquals(view.func, reply_topic)

    def test_form_contains_csrf_token_field(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_response_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, PostForm)

    def test_form_inputs_contains_csrf_and_message_fields(self):
        self.assertContains(self.response, "<input", 1)
        self.assertContains(self.response, "<textarea", 1)


class SuccessfulReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(
            self.url, {"message": "hello, world!"}
        )

    def test_valid_form_submission_should_redirect_the_user(self):
        topic_posts_url = reverse(
            "board:topic_posts",
            kwargs={"pk": self.board.pk, "topic_pk": self.topic.pk},
        )
        self.assertRedirects(self.response, topic_posts_url)

    def test_reply_created_after_valid_form_submission(self):
        self.assertEquals(Post.objects.count(), 2)


class InvalidReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_should_return_to_the_same_page(self):
        self.assertEquals(self.response.status_code, 200)

    def test_should_return_to_the_same_page_with_form_errors(self):
        form = self.response.context.get("form")
        self.assertTrue(form.errors)
