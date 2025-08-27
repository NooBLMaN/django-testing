from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser',
                                            password='123123')
        cls.other_user = User.objects.create_user(username='otheruser',
                                                  password='321321')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.user, slug='test-note')

    def test_pages_availability_for_auth_user(self):

        self.client.force_login(self.user)
        urls_status_pairs = (
            ('notes:list', 200),
            ('notes:add', 200),
            ('notes:success', 200),
        )
        for name, expected_status in urls_status_pairs:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_pages_availability_for_author(self):

        self.client.force_login(self.user)
        author_urls = (
            ('notes:detail', {'slug': self.note.slug}),
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
        )
        for name, kwargs in author_urls:
            with self.subTest(user='author', name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

        self.client.force_login(self.other_user)
        for name, kwargs in author_urls:
            with self.subTest(user='other', name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)

    def test_pages_availability(self):

        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        # Для URL, требующих slug заметки
        note_urls = ('notes:detail', 'notes:edit', 'notes:delete')
        # Для URL без параметров
        simple_urls = ('notes:add', 'notes:success', 'notes:list')

        for name in note_urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': 'test-slug'})
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

        for name in simple_urls:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
