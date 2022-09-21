from django.forms import ModelForm
from .models import Post


class PostForm(ModelForm):
    class Meta():
        model = Post
        fields = ['text', 'group']
        labels = {'text': 'Текст поста', 'group': 'Группа поста'}
        help_text = {'text': 'Текст нового поста',
                     'group': 'Группа которой будет присвоен пост'}
