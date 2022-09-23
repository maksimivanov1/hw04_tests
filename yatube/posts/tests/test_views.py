from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post


User = get_user_model()


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='max1',
                                            email='test1@mail.ru',
                                            password='test_pass',),
            text='Тестовая запись для создания 1 поста',
            group=Group.objects.create(
                title='Заголовок для 1 тестовой группы',
                slug='test-slug1'))

        cls.post2 = Post.objects.create(
            author=User.objects.create_user(username='max2',
                                            email='test2@mail.ru',
                                            password='test_pass',),
            text='Тестовая запись для создания 2 поста',
            id=3,
            group=Group.objects.create(
                title='Заголовок для 2 тестовой группы',
                slug='test-slug2'))

        cls.user_author = User.objects.create_user(username='Author')
        cls.author = Client()
        cls.author.force_login(cls.user_author)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='max888')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def context_check(self, post):
        """Функция проверки атрибутов контекста."""
        self.assertEqual(post.author, self.post2.author)
        self.assertEqual(post.text, self.post2.text)
        self.assertEqual(post.group, self.post2.group)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:groups', kwargs={'slug': self.post2.group.slug})
            ),
            'posts/create_post.html': reverse('posts:post_create')
        }
        for template, name in templates_pages_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(page_obj)
        self.assertGreater(len(page_obj), 0)
        first_object = response.context["page_obj"][0]
        self.assertIsNotNone(first_object)
        self.context_check(first_object)

    def test_group_pages_show_correct_context(self):
        """Шаблон groups сформирован с правильным контекстом."""
        response = self.authorized_client.\
            get(reverse('posts:groups',
                        kwargs={'slug': self.post2.group.slug}))
        first_object_group = response.context["group"]
        first_object_post = response.context["page_obj"][0]
        self.assertIsNotNone(first_object_post)
        self.assertIsNotNone(first_object_group)
        self.assertEqual(first_object_group.title, self.post2.group.title)
        self.assertEqual(first_object_group.slug, self.post2.group.slug)
        self.context_check(first_object_post)

    def test_post_in_another_group(self):
        """Пост не попал в другую группу."""
        response = self.authorized_client.get(
            reverse('posts:groups', kwargs={'slug': self.post.group.slug}))
        first_object = response.context["page_obj"][0]
        self.assertIsNotNone(first_object)
        self.assertIsNot(first_object.text, self.post2.text)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username':
                                             self.post2.author.username}))
        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(page_obj)
        self.assertGreater(len(page_obj), 0)
        first_object = response.context["page_obj"][0]
        self.assertIsNotNone(first_object)
        self.context_check(first_object)

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.author.\
            get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': self.post2.id})))
        first_object = response.context['post']
        self.context_check(first_object)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='max',
                                              email='test@mail.ru',
                                              password='test_pass',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test-slug2',
            description='Тестовое описание')
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='max888')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        """На первую страницу выводится 10 постов."""
        list_urls = {
            reverse("posts:index"): "index",
            reverse("posts:groups", kwargs={"slug": self.group.slug}): "group",
            reverse("posts:profile",
                    kwargs={"username": self.author.username}): "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_posts(self):
        """На вторую страницу выводитcя 3 поста."""
        list_urls = {
            reverse("posts:index") + "?page=2": "index",
            reverse("posts:groups",
                    kwargs={"slug": self.group.slug}) + "?page=2":
            "group",
            reverse("posts:profile",
                    kwargs={"username": self.author.username}) + "?page=2":
            "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context['page_obj']), 3)
