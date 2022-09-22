from http import HTTPStatus
import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='max')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='slagtest_1',
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='slagtest_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост 1',
        )
        cls.names_and_args = (
            ('posts:index', None),
            ('posts:groups', (cls.group.slug,)),
            ('posts:profile', (cls.user.username,)),
            ('posts:post_detail', (cls.post.id,)),
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        if Post.objects.count() > 0:
            Post.objects.all().delete()
        post_count = Post.objects.count()

        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
            
        )
        post = Post.objects.first()
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'После отправки новой формы число постов не изменилось!'
        )
        self.assertEqual(
            post.author,
            self.user,
            'Пользователь не совподает!'
        )
        self.assertEqual(
            post.text,
            form_data['text'],
            'Текст не совподает!'
        )
        self.assertEqual(
            post.group.id,
            form_data['group'],
            'Группа не совпадает!'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post_count = Post.objects.count()
        self.assertEqual(
            post_count,
            1,
            "Кроме тестового поста в базе имеются другие записи!"
        )
        form_data_edit = {
            'text': 'Редактируем тестовый пост',
            'group': self.group_2.id,
        }
        response_edit = self.authorized_author.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data_edit,
            follow=True
        )
        self.assertRedirects(
            response_edit,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(
            Post.objects.count(),
            post_count,
            'После редактирования поста, количество постов изменилось!'
        )
        post = Post.objects.first()
        self.assertEqual(
            post.author,
            self.post.author,
            'Пользователь не совподает!'
        )
        self.assertEqual(
            post.text,
            form_data_edit['text'],
            'Текст не совподает!'
        )
        self.assertEqual(
            post.group.pk,
            form_data_edit['group'],
            'Группа не совпадает!'
        )

        self.assertEqual(response_edit.status_code, HTTPStatus.OK)

        response = self.authorized_author.get(
            reverse('posts:groups', args=(self.group.slug,))
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Страница старой группы не доступна!'
        )

    def test_guest_not_create_post(self):
        """
        Проверяем, что не авторизованный пользователь
        не сможет создать пост.
        """
        AUTH_LOG_PAGE = "/auth/login/?next="

        if Post.objects.count() > 0:
            Post.objects.all().delete()
        post_count = Post.objects.count()
        form_data = {
            'text': 'Попытка гостя оставить пост',
            'group': self.group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'{AUTH_LOG_PAGE}{reverse("posts:post_create")}'
        )
        self.assertEqual(Post.objects.count(), post_count)
