from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNoteList(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser',
                                            password='password')
        cls.another_user = User.objects.create_user(username='user2',
                                                    password='password2')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.user, slug='test-note')
        cls.another_note = Note.objects.create(title='Заголовок2',
                                               text='Текст2',
                                               author=cls.another_user,
                                               slug='test-note2')

    def test_note_in_list(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])

    def test_user_sees_only_own_notes(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertNotIn(self.another_note, object_list)

    def test_another_user_notes_not_visible(self):
        self.client.login(username='user2', password='password2')
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.another_note, object_list)
        self.assertNotIn(self.note, object_list)

    def test_create_note_page_contains_form(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, NoteForm)
        self.assertIsNone(form.instance.pk)

    def test_edit_note_page_contains_form(self):
        self.client.login(username='testuser', password='password')
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.get(url)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertEqual(form.instance.pk, self.note.pk)
