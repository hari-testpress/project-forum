from django.db import models
from django.contrib.auth.models import User

from django.utils.html import mark_safe
from markdown import markdown

import math


class Board(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by("-created_at").last()


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, related_name="topics", on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name="topics", on_delete=models.CASCADE)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_page_count(self):
        posts_per_page = 2
        pages = self.posts.count() / posts_per_page
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        maximum_visible_page = 6
        if count is None:
            count = self.get_page_count()
        return count > maximum_visible_page

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name="posts", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    created_by = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(
        User, null=True, related_name="+", on_delete=models.CASCADE
    )

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode="escape"))
