from django.urls import reverse
from django.test import TestCase
from django.urls import resolve
from .models import Board
from .views import index, board_topics


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
