from http import HTTPStatus

from django.urls import reverse

from notes.tests.test_content import BaseNoteList


class TestRoutes(BaseNoteList):

    def test_pages_status_codes(self):
        """Тест статус кодов для разных пользователей и страниц"""
        test_cases = [
            # Анонимный пользователь
            (None, 'notes:home', None, HTTPStatus.OK),
            (None, 'users:login', None, HTTPStatus.OK),
            (None, 'users:signup', None, HTTPStatus.OK),
            (None, 'notes:list', None, HTTPStatus.FOUND),
            # redirect to login
            (None, 'notes:add', None, HTTPStatus.FOUND),
            # redirect to login
            (None, 'notes:success', None, HTTPStatus.FOUND),
            # redirect to login
            (None, 'notes:detail', {'slug': self.note.slug}, HTTPStatus.FOUND),
            # redirect
            (None, 'notes:edit', {'slug': self.note.slug}, HTTPStatus.FOUND),
            # redirect
            (None, 'notes:delete', {'slug': self.note.slug}, HTTPStatus.FOUND),
            # redirect

            # Авторизованный пользователь (не автор)
            (self.reader, 'notes:list', None, HTTPStatus.OK),
            (self.reader, 'notes:add', None, HTTPStatus.OK),
            (self.reader, 'notes:success', None, HTTPStatus.OK),
            (self.reader, 'notes:detail', {'slug': self.note.slug},
             HTTPStatus.NOT_FOUND),
            (self.reader, 'notes:edit', {'slug': self.note.slug},
             HTTPStatus.NOT_FOUND),
            (self.reader, 'notes:delete', {'slug': self.note.slug},
             HTTPStatus.NOT_FOUND),

            # Автор заметки
            (self.author, 'notes:list', None, HTTPStatus.OK),
            (self.author, 'notes:add', None, HTTPStatus.OK),
            (self.author, 'notes:success', None, HTTPStatus.OK),
            (self.author, 'notes:detail', {'slug': self.note.slug},
             HTTPStatus.OK),
            (self.author, 'notes:edit', {'slug': self.note.slug},
             HTTPStatus.OK),
            (self.author, 'notes:delete', {'slug': self.note.slug},
             HTTPStatus.OK),
        ]

        for user, url_name, kwargs, expected_status in test_cases:
            with self.subTest(user=user.username if user
                              else 'anonymous', url=url_name):
                # Авторизуем пользователя если указан
                if user:
                    self.client.force_login(user)
                else:
                    self.client.logout()

                url = reverse(url_name, kwargs=kwargs)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        """Тест редиректов для анонимного пользователя"""
        redirect_cases = [
            # URL с параметром slug
            ('notes:detail', {'slug': 'test-slug'}),
            ('notes:edit', {'slug': 'test-slug'}),
            ('notes:delete', {'slug': 'test-slug'}),
            # URL без параметров
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        ]

        for url_name, kwargs in redirect_cases:
            with self.subTest(url=url_name):
                url = reverse(url_name, kwargs=kwargs)
                expected_redirect = f"{self.LOGIN_URL}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
