from http import HTTPStatus

from notes.models import Note
from notes.tests.test_content import BaseNoteList


class TestLogic(BaseNoteList):

    def setUp(self):
        """Регистрируем пользователя один раз в начале тестирования"""
        self.client.login(username='author', password='password')

    def test_user_can_create_note(self):
        """Тест возможности создания заметки авторизованным пользователем"""
        new_note_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': 'new-note'
        }

        response = self.client.post(self.ADD_URL, data=new_note_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Note.objects.filter(slug='new-note').exists())

    def test_anonymous_user_cannot_create_note(self):
        """Тест невозможности создания записи анонимному пользователю"""
        self.client.logout()

        initial_count = Note.objects.count()

        note_data = {
            'title': 'Анонимная заметка',
            'text': 'Текст анонимной заметки',
            'slug': 'anonymous-note'
        }

        response = self.client.post(self.ADD_URL, data=note_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(response.url.startswith(self.LOGIN_URL))

        final_count = Note.objects.count()
        self.assertEqual(initial_count, final_count)
        self.assertFalse(Note.objects.filter(slug='anonymous-note').exists())

    def test_not_unique_slug(self):
        """Тест невозможности создания двух заметок с одиноковым slug"""
        second_note_data = {
            'title': 'Другая заметка',
            'text': 'Текст заметки',
            'slug': 'test-note'
        }

        response = self.client.post(self.ADD_URL, data=second_note_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.filter(slug='test-note').count(), 1)

    def test_auto_slug_generation(self):
        """Тест формирования автоматического slug, если slug не заполнен"""
        note_data = {
            'title': 'Other note',
            'text': 'Текст заметки',
            'slug': ''
        }

        response = self.client.post(self.ADD_URL, data=note_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        note = Note.objects.get(title='Other note')
        self.assertTrue(note.slug.startswith('other-note'))

    def test_user_can_edit_own_note(self):
        """Тест возможности редактирования собственной заметки"""
        edit_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'updated-note'
        }

        response = self.client.post(self.EDIT_AUTHOR_NOTE_URL, data=edit_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Обновленный заголовок')
        self.assertEqual(self.note.slug, 'updated-note')

    def test_user_cannot_edit_other_user_note(self):
        """Тест невозможности редактирования чужой заметки"""
        response = self.client.get(self.EDIT_READER_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_can_delete_own_note(self):
        """Тест возможности удалять собственные заметки"""
        response = self.client.delete(self.DELETE_AUTHOR_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(slug='test-note').exists())

    def test_user_cannot_delete_other_user_note(self):
        """Тест невозможности удалять чужие заметки"""
        response = self.client.delete(self.DELETE_READER_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(slug='test-note2').exists())
