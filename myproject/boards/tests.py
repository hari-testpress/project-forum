from django.urls import reverse
from django.test import TestCase
from django.urls import resolve
from .models import Board
from .views import index


class IndexViewTests(TestCase):
    def test_status_code_is_200(self):
        url = reverse("index")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_root_url_resolves_index_view(self):
        view = resolve("/")
        self.assertEquals(view.func, index)
