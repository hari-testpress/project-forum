from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from .forms import NewTopicForm
from .models import Board, Post


def index(request):
    boards = Board.objects.all()
    return render(request, "index.html", {"boards": boards})


def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    return render(request, "topics.html", {"board": board})


def add_new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()
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
