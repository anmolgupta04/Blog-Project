from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.blog.models import Comment, Post, Tag


class Command(BaseCommand):
    help = "Seed the database with demo users, tags, posts, and comments."

    def handle(self, *args, **options):
        user_model = get_user_model()

        author, created = user_model.objects.get_or_create(
            username="demoauthor",
            defaults={
                "email": "demoauthor@example.com",
                "first_name": "Demo",
                "last_name": "Author",
                "bio": "Writes about Django, shipping products, and clean web architecture.",
            },
        )
        if created:
            author.set_password("DemoPassword123")
            author.save()
            self.stdout.write(self.style.SUCCESS("Created demoauthor user."))

        editor, created = user_model.objects.get_or_create(
            username="editor",
            defaults={
                "email": "editor@example.com",
                "first_name": "Site",
                "last_name": "Editor",
                "bio": "Curates sample content for the StoryBoard demo application.",
            },
        )
        if created:
            editor.set_password("DemoPassword123")
            editor.save()
            self.stdout.write(self.style.SUCCESS("Created editor user."))

        tags = {}
        for name in ["Django", "Bootstrap", "Deployment", "Productivity", "Python"]:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags[name] = tag

        posts_data = [
            {
                "title": "Launching a Django Project with Confidence",
                "excerpt": "A practical checklist for getting from a blank repo to a solid deployable Django app.",
                "content": (
                    "Starting a Django project is easy, but starting one with reliable defaults takes intention. "
                    "This demo shows how to wire authentication, model relationships, reusable templates, static "
                    "assets, and deployment-aware settings into one maintainable project. By beginning with a "
                    "clear structure, you avoid painful rewrites later and keep your team moving with confidence."
                ),
                "author": author,
                "status": Post.Status.PUBLISHED,
                "tag_names": ["Django", "Python"],
            },
            {
                "title": "Designing Responsive Templates with Bootstrap 5",
                "excerpt": "Use the Django template language and Bootstrap together without sacrificing clarity.",
                "content": (
                    "Bootstrap 5 makes responsive layout work fast, but Django templates keep the app maintainable. "
                    "A base template, clear content blocks, and predictable component styling let you move quickly "
                    "while preserving readability. The result is a project that feels polished on mobile and desktop."
                ),
                "author": editor,
                "status": Post.Status.PUBLISHED,
                "tag_names": ["Bootstrap", "Django"],
            },
            {
                "title": "From Localhost to Linux: Preparing for Deployment",
                "excerpt": "Gunicorn, Nginx, collectstatic, and environment variables form a dependable deployment path.",
                "content": (
                    "Production deployment is less about magic and more about layering the right responsibilities. "
                    "Gunicorn serves the Django application, Nginx handles reverse proxying and static delivery, "
                    "and environment variables keep secrets out of source control. This project includes sample "
                    "files so the path from development to Linux hosting stays straightforward."
                ),
                "author": author,
                "status": Post.Status.PUBLISHED,
                "tag_names": ["Deployment", "Django", "Bootstrap"],
            },
        ]

        for post_data in posts_data:
            post, _ = Post.objects.update_or_create(
                title=post_data["title"],
                defaults={
                    "excerpt": post_data["excerpt"],
                    "content": post_data["content"],
                    "author": post_data["author"],
                    "status": post_data["status"],
                },
            )
            post.tags.set([tags[name] for name in post_data["tag_names"]])

        first_post = Post.objects.filter(status=Post.Status.PUBLISHED).first()
        if first_post:
            Comment.objects.get_or_create(
                post=first_post,
                author=editor,
                content="This seeded comment helps demonstrate the detail page discussion flow.",
            )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully."))
