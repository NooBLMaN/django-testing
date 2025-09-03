from http import HTTPStatus

from django.test import Client

from notes.models import Note
from notes.tests.conftest import BaseNoteList


class TestLogic(BaseNoteList):

    def test_user_can_create_note(self):
        """Тест возможности создания заметки авторизованным пользователем"""
        initial_count = Note.objects.count()

        response = self.client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        final_count = Note.objects.count()
        self.assertEqual(final_count, initial_count + 1)

        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_anonymous_user_cannot_create_note(self):
        """Тест невозможности создания записи анонимному пользователю"""
        anon_client = Client()
        initial_count = Note.objects.count()

        response = anon_client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(response.url.startswith(self.LOGIN_URL))

        final_count = Note.objects.count()
        self.assertEqual(initial_count, final_count)

    def test_not_unique_slug(self):
        """Тест невозможности создания двух заметок с одиноковым slug"""
        initial_count = Note.objects.count()

        second_note_data = {
            'title': 'Другая заметка',
            'text': 'Текст заметки',
            'slug': self.note.slug
        }

        response = self.client.post(self.ADD_URL, data=second_note_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        final_count = Note.objects.count()
        self.assertEqual(final_count, initial_count)
        self.assertEqual(Note.objects.filter(slug=self.note.slug).count(), 1)

    def test_auto_slug_generation(self):
        """Тест формирования автоматического slug, если slug не заполнен"""
        initial_count = Note.objects.count()

        note_data = {
            'title': 'Other note',
            'text': 'Текст заметки',
            'slug': ''
        }

        response = self.client.post(self.ADD_URL, data=note_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        final_count = Note.objects.count()
        self.assertEqual(final_count, initial_count + 1)

        note = Note.objects.get(title='Other note')
        self.assertTrue(note.slug.startswith('other-note'))

    def test_user_can_edit_own_note(self):
        """Тест возможности редактирования собственной заметки"""
        original_title = self.note.title

        edit_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'updated-note'
        }

        response = self.client.post(self.EDIT_AUTHOR_NOTE_URL, data=edit_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        updated_note = Note.objects.get(id=self.note.id)

        self.assertEqual(updated_note.title, edit_data['title'])
        self.assertEqual(updated_note.text, edit_data['text'])
        self.assertEqual(updated_note.slug, edit_data['slug'])

        self.assertNotEqual(updated_note.title, original_title)

    def test_user_cannot_edit_other_user_note(self):
        """Тест невозможности редактирования чужой заметки"""
        initial_count = Note.objects.count()

        original_title = self.another_note.title
        original_text = self.another_note.text
        original_slug = self.another_note.slug

        response = self.client.get(self.EDIT_READER_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        unchanged_note = Note.objects.get(id=self.another_note.id)

        final_count = Note.objects.count()
        self.assertEqual(final_count, initial_count)

        self.assertEqual(unchanged_note.title, original_title)
        self.assertEqual(unchanged_note.text, original_text)
        self.assertEqual(unchanged_note.slug, original_slug)

    def test_user_can_delete_own_note(self):
        """Тест возможности удалять собственные заметки"""
        initial_count = Note.objects.count()

        response = self.client.delete(self.DELETE_AUTHOR_NOTE_URL)
        final_count = Note.objects.count()
        self.assertEqual(final_count, initial_count - 1)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cannot_delete_other_user_note(self):
        """Тест невозможности удалять чужие заметки"""
        initial_count = Note.objects.count()

        original_title = self.another_note.title
        original_text = self.another_note.text
        original_slug = self.another_note.slug
        original_author = self.another_note.author

        response = self.client.delete(self.DELETE_READER_NOTE_URL)
        final_count = Note.objects.count()
        self.assertEqual(final_count, initial_count)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())

        unchanged_note = Note.objects.get(id=self.another_note.id)

        self.assertEqual(unchanged_note.title, original_title)
        self.assertEqual(unchanged_note.text, original_text)
        self.assertEqual(unchanged_note.slug, original_slug)
        self.assertEqual(unchanged_note.author, original_author)
