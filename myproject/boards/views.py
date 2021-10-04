from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .forms import NewTopicForm, PostForm
from .models import Board, Post, Topic


def index(request):
    boards = Board.objects.all()
    return render(request, "index.html", {"boards": boards})


def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    topics = board.topics.order_by("-created_at").annotate(
        replies=Count("posts") - 1
    )
    return render(request, "topics.html", {"board": board, "topics": topics})


@login_required
def add_new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = request.user
    if request.method == "POST":
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get("message"),
                topic=topic,
                created_by=user,
            )
            return redirect("board:board_topics", pk=board.pk)
    else:
        form = NewTopicForm()
    return render(request, "new_topic.html", {"board": board, "form": form})


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views_count += 1
    topic.save()
    return render(request, "topic_posts.html", {"topic": topic})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect("board:topic_posts", pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, "reply_topic.html", {"topic": topic, "form": form})
