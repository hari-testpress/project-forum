from django.urls import reverse
from django.test import TestCase
from django.urls import resolve
from django.contrib.auth.models import User

from .views import index, board_topics, add_new_topic
from .models import Board, Topic, Post
from .forms import NewTopicForm


class IndexViewTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(
            name="Django", description="Django board."
        )
        url = reverse("index")
        self.response = self.client.get(url)

    def test_status_code_is_200(self):
        self.assertEquals(self.response.status_code, 200)

    def test_root_url_resolves_index_view(self):
        view = resolve("/")
        self.assertEquals(view.func, index)

    def test_index_view_contains_link_to_topics_page(self):
        board_topics_url = reverse(
            "board:board_topics", kwargs={"pk": self.board.pk}
        )
        self.assertContains(
            self.response, 'href="{0}"'.format(board_topics_url)
        )


class BoardTopicsTests(TestCase):
    def setUp(self):
        Board.objects.create(name="Django", description="Django board.")

    def test_should_return_200_for_the_exist_board(self):
        url = reverse("board:board_topics", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_should_return_404_for_the_non_exist_board(self):
        url = reverse("board:board_topics", kwargs={"pk": 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve("/boards/1/")
        self.assertEquals(view.func, board_topics)

    def test_board_topics_view_contains_link_back_to_homepage(self):
        board_topics_url = reverse("board:board_topics", kwargs={"pk": 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse("index")
        self.assertContains(response, 'href="{0}"'.format(homepage_url))


class AddNewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name="Django", description="Django board.")
        User.objects.create_user(
            username="john", email="john@doe.com", password="123"
        )

    def test_new_topic_view_should_return_200_for_the_exist_board(self):
        url = reverse("board:add_new_topic", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_view_should_return_404_for_the_non_exist_board(self):
        url = reverse("board:add_new_topic", kwargs={"pk": 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_url_resolves_add_new_topic_view(self):
        view = resolve("/boards/1/new_topic")
        self.assertEquals(view.func, add_new_topic)

    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        new_topic_url = reverse("board:add_new_topic", kwargs={"pk": 1})
        board_topics_url = reverse("board:board_topics", kwargs={"pk": 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    def test_add_new_topic_response_contains_csrf_token(self):
        url = reverse("board:add_new_topic", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_add_new_topic_response_contains_form(self):
        url = reverse("board:add_new_topic", kwargs={"pk": 1})
        response = self.client.get(url)
        form = response.context.get("form")
        self.assertIsInstance(form, NewTopicForm)

    def test_add_new_topic_with_valid_post_data_stores_topic_in_the_database(
        self,
    ):
        url = reverse("board:add_new_topic", kwargs={"pk": 1})
        data = {
            "subject": "Test title",
            "message": "Lorem ipsum dolor sit amet",
        }
        self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_add_new_topic_view_should_redirect_invalid_post_data_with_errors(
        self,
    ):
        url = reverse("board:add_new_topic", kwargs={"pk": 1})
        response = self.client.post(url, {})
        form = response.context.get("form")
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_add_new_topic_view_with_empty_fields_should_not_store_the_topic(
        self,
    ):
        url = reverse("board:add_new_topic", kwargs={"pk": 1})
        data = {"subject": "", "message": ""}
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())
