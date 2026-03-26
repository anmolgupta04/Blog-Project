from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import CommentForm, PostForm
from .models import Comment, Post, Tag


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        published_posts = (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .select_related("author")
            .prefetch_related("tags")
        )
        featured_post = published_posts.first()
        context["featured_post"] = featured_post
        context["latest_posts"] = (
            published_posts.exclude(pk=featured_post.pk)[:3]
            if featured_post
            else published_posts[:3]
        )
        context["tag_list"] = Tag.objects.all()[:8]
        return context


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        queryset = (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .select_related("author")
            .prefetch_related("tags")
        )
        query = self.request.GET.get("q", "").strip()
        tag_slug = self.request.GET.get("tag", "").strip()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(excerpt__icontains=query)
                | Q(content__icontains=query)
                | Q(tags__name__icontains=query)
                | Q(author__username__icontains=query)
            ).distinct()

        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_list"] = Tag.objects.all()
        context["current_query"] = self.request.GET.get("q", "").strip()
        context["current_tag"] = self.request.GET.get("tag", "").strip()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = (
            Post.objects.select_related("author")
            .prefetch_related(
                "tags",
                Prefetch(
                    "comments",
                    queryset=Comment.objects.filter(active=True).select_related("author"),
                ),
            )
        )
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(status=Post.Status.PUBLISHED) | Q(author=self.request.user)
            ).distinct()
        return queryset.filter(status=Post.Status.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        context["comments"] = self.object.comments.all()
        context["related_posts"] = (
            Post.objects.filter(status=Post.Status.PUBLISHED, tags__in=self.object.tags.all())
            .exclude(pk=self.object.pk)
            .select_related("author")
            .distinct()[:3]
        )
        return context


class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.get_object().author or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to modify this post.")
        return redirect("post_detail", slug=self.get_object().slug)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Your post has been created successfully.")
        return response


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your post has been updated.")
        return response


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("post_list")

    def form_valid(self, form):
        messages.success(self.request, "The post has been deleted.")
        return super().form_valid(form)


@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, "Your comment has been added.")
    else:
        for error in form.errors.get("content", []):
            messages.error(request, error)

    return HttpResponseRedirect(post.get_absolute_url())
