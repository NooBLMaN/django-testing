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
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user,
            slug='test-note'
        )

    def test_pages_availability_for_different_users(self):
        """Тест доступности страниц для разных типов пользователей."""
        test_cases = [
            # Анонимные пользователи
            {
                'user': None,
                'urls': [
                    ('notes:home', None, HTTPStatus.OK),
                    ('users:login', None, HTTPStatus.OK),
                    ('users:signup', None, HTTPStatus.OK),
                ]
            },
            # Авторизованные пользователи (общие страницы)
            {
                'user': self.user,
                'urls': [
                    ('notes:list', None, HTTPStatus.OK),
                    ('notes:add', None, HTTPStatus.OK),
                    ('notes:success', None, HTTPStatus.OK),
                ]
            },
            # Автор заметки
            {
                'user': self.user,
                'urls': [
                    ('notes:detail', {'slug': self.note.slug}, HTTPStatus.OK),
                    ('notes:edit', {'slug': self.note.slug}, HTTPStatus.OK),
                    ('notes:delete', {'slug': self.note.slug}, HTTPStatus.OK),
                ]
            },
            # Другой пользователь (не автор)
            {
                'user': self.other_user,
                'urls': [
                    ('notes:detail', {'slug': self.note.slug},
                     HTTPStatus.NOT_FOUND),
                    ('notes:edit', {'slug': self.note.slug},
                     HTTPStatus.NOT_FOUND),
                    ('notes:delete', {'slug': self.note.slug},
                     HTTPStatus.NOT_FOUND),
                ]
            }
        ]

        for case in test_cases:
            if case['user']:
                self.client.force_login(case['user'])
            else:
                self.client.logout()

            for name, kwargs, expected_status in case['urls']:
                with self.subTest(user=case['user'], name=name, kwargs=kwargs):
                    url = reverse(name, kwargs=kwargs)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректов для анонимных пользователей."""
        login_url = reverse('users:login')

        # URL с параметрами (требуют slug)
        note_urls = [
            ('notes:detail', {'slug': 'test-slug'}),
            ('notes:edit', {'slug': 'test-slug'}),
            ('notes:delete', {'slug': 'test-slug'}),
        ]

        # URL без параметров
        simple_urls = [
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        ]

        # Тестируем URL с параметрами
        for name, kwargs in note_urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

        # Тестируем URL без параметров
        for name, kwargs in simple_urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
