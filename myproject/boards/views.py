from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator

from .forms import NewTopicForm, PostForm
from .models import Board, Post, Topic


def index(request):
    boards = Board.objects.all()
    return render(request, "index.html", {"boards": boards})


class TopicListView(ListView):
    model = Topic
    context_object_name = "topics"
    template_name = "topics.html"
    paginate_by = 2

    def get_context_data(self, **kwargs):
        kwargs["board"] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get("pk"))
        queryset = self.board.topics.order_by("-created_at").annotate(
            replies=Count("posts") - 1
        )
        return queryset


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


class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "topic_posts.html"
    paginate_by = 3

    def get_context_data(self, **kwargs):
        self.topic.views += 1
        self.topic.save()
        kwargs["topic"] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(
            Topic,
            board__pk=self.kwargs.get("pk"),
            pk=self.kwargs.get("topic_pk"),
        )
        queryset = self.topic.posts.order_by("created_at")
        return queryset


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


@method_decorator(login_required, name="dispatch")
class PostUpdateView(UpdateView):
    model = Post
    fields = ("message",)
    template_name = "edit_post.html"
    pk_url_kwarg = "post_pk"
    context_object_name = "post"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect(
            "board:topic_posts", pk=post.topic.board.pk, topic_pk=post.topic.pk
        )
