from django.test import TestCase, Client
from django.urls import reverse
from posts.models import User, Post, Group
from posts.forms import PostForm


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='test1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовая:)'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user_author,
            group=cls.group
        )
        cls.post_id = cls.post.id
        cls.form = PostForm()
        cls.posts_count = Post.objects.count()

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(PostFormTests.user_author)

    def test_create_post(self):
        """Успешное создание поста."""
        post_form_data = {
            'text': 'Текст из формы',
            'group': PostFormTests.group.id
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=post_form_data,
            follow=False
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.user_author}
            )
        )
        self.assertEqual(Post.objects.count(), PostFormTests.posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст из формы',
                group=PostFormTests.group
            ).exists()
        )

    # def test_post_edit(self):
    #     posts_count = Post.objects.count()
    #     form_data = {
    #         'text': 'Измененный текст',
    #     }
    #     response = self.authorized_author.post(
    #         reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
    #         data=form_data,
    #         follow=True
    #     )
    #     self.assertRedirects(response, reverse(
    #         'posts:post_detail', kwargs={'post_id': self.post.id}))
       
    #     self.assertEqual(
    #         Post.objects.get(self.post.id).text, form_data['text']
    #     )
    #     self.assertEqual(
    #         Post.objects.get(self.post.id).author, self.post.author
    #     )
    #     self.assertEqual(Post.objects.count(), posts_count)
