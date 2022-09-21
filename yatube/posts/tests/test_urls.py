from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='max888')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_author = User.objects.create_user(username='Author')
        cls.author = Client()
        cls.author.force_login(cls.user_author)

        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовая запись для создания нового поста',
            id=5)

        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug'
        )

    def test_pages(self):
        """ Страницы доступные всем """
        url_names = (
            '/',
            '/group/test_slug/',
            '/profile/Author/',

        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_for_authorized(self):
        """Страница /create доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/create_post.html': '/create/',
            'posts/profile.html': '/profile/max888/',

        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_task_detail_pages_authorized_uses_correct_template(self):
        """URL-адреса используют шаблон posts/post_detail.html."""
        response = self.authorized_client.\
            get(reverse('posts:post_detail', kwargs={'post_id': 5}))
        self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_post_edit(self):
        """post_edit возвращает статус 200"""
        response = self.author.\
            get(reverse('posts:post_edit', kwargs={'post_id': 5}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_is_auth(self):
        response = self.authorized_client.\
            get(reverse('posts:post_detail', kwargs={'post_id': 5}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_no_auth(self):
        response = self.guest_client.\
            get(reverse('posts:post_detail', kwargs={'post_id': 5}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
