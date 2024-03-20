from django import forms

from blog.models import Post
from main.forms import FormStyleMixin


class PostForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('slug', 'is_published', 'count_of_view')