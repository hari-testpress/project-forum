from django.urls import path
from . import views

app_name = "board"

urlpatterns = [
    path("<int:pk>/", views.TopicListView.as_view(), name="board_topics"),
    path("<int:pk>/new_topic", views.add_new_topic, name="add_new_topic"),
    path(
        "<int:pk>/topics/<int:topic_pk>/",
        views.PostListView.as_view(),
        name="topic_posts",
    ),
    path(
        "<int:pk>/topics/<int:topic_pk>/reply/",
        views.reply_topic,
        name="reply_topic",
    ),
    path(
        "<int:pk>/topics/<int:topic_pk>/posts/<int:post_pk>/edit/",
        views.PostUpdateView.as_view(),
        name="edit_post",
    ),
]
