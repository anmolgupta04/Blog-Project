from django import forms

from .models import Comment, Post


class BootstrapFormMixin:
    def _apply_bootstrap_classes(self):
        for field in self.fields.values():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"
            if isinstance(field.widget, forms.SelectMultiple):
                css_class = "form-select"

            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()
            if field.required:
                field.widget.attrs.setdefault("required", "required")


class PostForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "excerpt", "content", "status", "tags", "cover_image"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Enter a clear, engaging title"}
            ),
            "excerpt": forms.TextInput(
                attrs={"placeholder": "Short summary for cards and previews"}
            ),
            "content": forms.Textarea(
                attrs={
                    "rows": 10,
                    "placeholder": "Write the full post content here...",
                }
            ),
            "status": forms.Select(),
            "tags": forms.SelectMultiple(attrs={"size": 5}),
            "cover_image": forms.ClearableFileInput(),
        }
        help_texts = {
            "tags": "Hold Ctrl (Windows) or Command (Mac) to select multiple tags.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 5:
            raise forms.ValidationError("The title must be at least 5 characters long.")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if len(content) < 50:
            raise forms.ValidationError("The content must be at least 50 characters long.")
        return content


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Share a thoughtful comment...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if len(content) < 5:
            raise forms.ValidationError("Comments must be at least 5 characters long.")
        return content
