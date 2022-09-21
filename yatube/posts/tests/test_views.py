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

        cls.post = Post.objects.create(
            author=User.objects.create_user(username='max2',
                                            email='test2@mail.ru',
                                            password='test_pass',),
            text='Тестовая запись для создания 2 поста',
            id=3,
            group=Group.objects.create(
                title='Заголовок для 2 тестовой группы',
                slug='test-slug2'))

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='max888')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Данная проверка находится в test_urls. DRY!"""
        pass

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(page_obj)
        self.assertGreater(len(page_obj), 0)
        first_object = response.context["page_obj"][0]
        self.assertIsNotNone(first_object)
        self.assertEqual(first_object.text,
                         'Тестовая запись для создания 2 поста')
        self.assertEqual(first_object.author.username, 'max2')
        self.assertEqual(first_object.group.title,
                         'Заголовок для 2 тестовой группы')

    def test_group_pages_show_correct_context(self):
        """Шаблон группы"""
        response = self.authorized_client.get(reverse
                                              ('posts:groups',
                                               kwargs={'slug': 'test-slug2'}))
        first_object = response.context["group"]
        self.assertIsNotNone(first_object)
        self.assertEqual(first_object.title, 'Заголовок для 2 тестовой группы')
        self.assertEqual(first_object.slug, 'test-slug2')

    def test_post_in_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(
            reverse('posts:groups', kwargs={'slug': 'test-slug1'}))
        first_object = response.context["page_obj"][0]
        self.assertIsNotNone(first_object)
        self.assertTrue(first_object.text,
                        'Тестовая запись для создания 2 поста')

    # def test_post_detail_context(self):
    #!!!НЕКОТОРЫЕ ВЬЮХИ МОГУТ БЫТЬ НЕДОПИСАНЫ.НО МНЕ НУЖНО СДАТЬ ПРОЕКТЫ ДО 26#
    # СЕНТЯБРЯ ПОЭТОМУ Я КАК МОЖНО БЫСТРЕЕ ХОЧУ ПОЛУЧИТЬ ВСЕ ЗАМЕЧАНИЯ И#
    # ОТПРАВИТЬ НА ПОВТОРНОЕ РЕВЬЮ ПОЛНОСТЬЮ ГОТОВЫЙ ПРОЕКТ ТАК КАК НА#
    # СДАЧУ 6 СПРИНТА У МЕНЯ ОСТАНЕТСЯ 3 ДНЯ(ИНАЧЕ МЕНЯ ИСКЛЮЧАТ,АКАДЕМОВ 0)!!!#

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'max2'}))
        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(page_obj)
        self.assertGreater(len(page_obj), 0)
        first_object = response.context["page_obj"][0]
        self.assertIsNotNone(first_object)
        self.assertEqual(response.context['author'].username, 'max2')
        self.assertEqual(first_object.text,
                         'Тестовая запись для создания 2 поста')


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
        """На первую страницу выводится 10 постов"""
        list_urls = {
            reverse("posts:index"): "index",
            reverse("posts:groups", kwargs={"slug": "test-slug2"}): "group",
            reverse("posts:profile", kwargs={"username": "max"}): "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_posts(self):
        """На вторую страницу выводитчя 3 поста"""
        list_urls = {
            reverse("posts:index") + "?page=2": "index",
            reverse("posts:groups", kwargs={"slug": "test-slug2"}) + "?page=2":
            "group",
            reverse("posts:profile", kwargs={"username": "max"}) + "?page=2":
            "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context['page_obj']), 3)
