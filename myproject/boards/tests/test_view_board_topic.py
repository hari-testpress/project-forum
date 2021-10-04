from django.urls import reverse, resolve
from django.test import TestCase

from ..views import TopicListView
from ..models import Board


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
        self.assertEquals(view.func.view_class, TopicListView)

    def test_board_topics_view_contains_link_back_to_homepage(self):
        board_topics_url = reverse("board:board_topics", kwargs={"pk": 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse("index")
        self.assertContains(response, 'href="{0}"'.format(homepage_url))
