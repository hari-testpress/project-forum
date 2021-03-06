from django.urls import path
from . import views

app_name = "board"

urlpatterns = [
    path("<int:pk>/", views.board_topics, name="board_topics"),
    path("<int:pk>/new_topic", views.add_new_topic, name="add_new_topic"),
    path(
        "<int:pk>/topics/<int:topic_pk>/",
        views.topic_posts,
        name="topic_posts",
    ),
    path(
        "<int:pk>/topics/<int:topic_pk>/reply/",
        views.reply_topic,
        name="reply_topic",
    ),
]
