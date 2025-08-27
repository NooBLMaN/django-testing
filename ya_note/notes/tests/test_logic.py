from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser',
                                            password='password')
        cls.other_user = User.objects.create_user(username='other_user',
                                                  password='password')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.user, slug='test-note')
        cls.other_note = Note.objects.create(title='Другой заголовок',
                                             text='Текст',
                                             author=cls.other_user,
                                             slug='test-note2')

    def test_user_can_create_note(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:add')

        new_note_data = {
            'title': 'Заметка без slug',
            'text': 'Текст заметки',
            'slug': ''
        }

        response = self.client.post(url, data=new_note_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(title='Заголовок').exists())

    def test_anonymous_user_cannot_create_note(self):
        url = reverse('notes:add')
        note_data = {
            'title': 'Анонимная заметка',
            'text': 'Текст анонимной заметки',
            'slug': 'anonymous-note'
        }

        response = self.client.post(url, data=note_data)

        self.assertIn(response.status_code, [302, 403])
        self.assertFalse(Note.objects.filter(slug='anonymous-note').exists())

    def test_not_unique_slug(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:add')
        second_note_data = {
            'title': 'Другая заметка',
            'text': 'Текст заметки',
            'slug': 'test-note'
        }

        response = self.client.post(url, data=second_note_data)
        self.assertNotEqual(response.status_code, 302)
        self.assertEqual(Note.objects.filter(slug='test-note').count(), 1)

    def test_auto_slug_generation(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:add')
        note_data = {
            'title': 'Other note',
            'text': 'Текст заметки',
            'slug': ''
        }

        response = self.client.post(url, data=note_data)
        self.assertEqual(response.status_code, 302)

        note = Note.objects.get(title='Other note')
        self.assertTrue(note.slug.startswith('other-note'))

    def test_user_can_edit_own_note(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:edit', args=[self.note.slug])

        edit_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'updated-note'
        }

        response = self.client.post(url, data=edit_data)

        self.assertEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Обновленный заголовок')
        self.assertEqual(self.note.slug, 'updated-note')

    def test_user_cannot_edit_other_user_note(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:edit', args=[self.other_note.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_can_delete_own_note(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(slug='test-note').exists())

    def test_user_cannot_delete_other_user_note(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:delete', args=[self.other_note.slug])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(slug='test-note2').exists())
