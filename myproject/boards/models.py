from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(
        Board, related_name="topics", on_delete=models.CASCADE
    )
    starter = models.ForeignKey(
        User, related_name="topics", on_delete=models.CASCADE
    )


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(
        Topic, related_name="posts", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    created_by = models.ForeignKey(
        User, related_name="posts", on_delete=models.CASCADE
    )
    updated_by = models.ForeignKey(
        User, null=True, related_name="+", on_delete=models.CASCADE
    )
