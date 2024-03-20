from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.utils.text import slugify
from transliterate import translit
from blog.forms import PostForm
from blog.services import get_cache_detail_post
from blog.models import Post


class PostListView(generic.ListView):
    model = Post
    extra_context = {
        "title": "My news"
    }

    template_name = 'post_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)
        return queryset


class PostDetailView(generic.DetailView):
    model = Post
    queryset = get_cache_detail_post()

    def get_object(self, queryset=None):
        object_item = super().get_object(queryset)
        object_item.increase_count_of_view()
        object_item.save()
        return object_item


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    form_class = PostForm
    success_url = reverse_lazy('blog:home')
    permission_required = 'blog.add_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        eng_title = translit(post.title, 'ru', reversed=True)
        post.slug = slugify(eng_title, allow_unicode=True)
        return super(PostCreateView, self).form_valid(form)


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    permission_required = 'blog.change_post'

    def get_success_url(self):
        return reverse('blog:blog_detail', kwargs={'slug': self.object.slug})


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    model = Post
    success_url = reverse_lazy('blog:home')
    permission_required = 'blog.delete_post'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)
        return queryset
