from django.urls import path

from .views import HomeView, PostCreateView, PostDeleteView, PostDetailView, PostListView, PostUpdateView, add_comment

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("posts/", PostListView.as_view(), name="post_list"),
    path("posts/new/", PostCreateView.as_view(), name="post_create"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("posts/<slug:slug>/edit/", PostUpdateView.as_view(), name="post_update"),
    path("posts/<slug:slug>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("posts/<slug:slug>/comments/add/", add_comment, name="add_comment"),
]
