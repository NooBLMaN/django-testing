from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class BaseNoteList(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='password'
        )
        cls.reader = User.objects.create_user(
            username='reader',
            password='password2'
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='test-note'
        )
        cls.another_note = Note.objects.create(
            title='Заголовок2',
            text='Текст2',
            author=cls.reader,
            slug='test-note2'
        )

        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.LOGIN_URL = reverse('users:login')
        cls.EDIT_AUTHOR_NOTE_URL = reverse('notes:edit', args=[cls.note.slug])
        cls.EDIT_READER_NOTE_URL = reverse('notes:edit',
                                           args=[cls.another_note.slug])
        cls.DELETE_AUTHOR_NOTE_URL = reverse('notes:delete',
                                             args=[cls.note.slug])
        cls.DELETE_READER_NOTE_URL = reverse('notes:delete',
                                             args=[cls.another_note.slug])


class TestAuthorNoteList(BaseNoteList):

    def setUp(self):
        """Регистрируем пользователя один раз в начале тестирования"""
        self.client.login(username='author', password='password')

    def test_note_in_list_for_author(self):
        """Тест проверки, что заметка автора присутствует в списке заметок"""
        response = self.client.get(self.LIST_URL)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])
        self.assertNotIn(self.another_note, response.context['object_list'])
        self.assertEqual(len(response.context['object_list']), 1)
        note_from_list = response.context['object_list'][0]
        self.assertEqual(note_from_list.title, 'Заголовок')
        self.assertEqual(note_from_list.text, 'Текст')
        self.assertEqual(note_from_list.slug, 'test-note')
        self.assertEqual(note_from_list.author, self.author)

    def test_another_user_notes_not_visible(self):
        """Тест, что пользователь не видит заметки другого пользователя"""
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.another_note, object_list)
        self.assertIn(self.note, object_list)

    def test_create_note_page_contains_form(self):
        """Тест, что страница создания имеет форму"""
        response = self.client.get(self.ADD_URL)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, NoteForm)

    def test_edit_note_page_contains_form(self):
        """Тест, что страница редактирования заметки имеет форму"""
        response = self.client.get(self.EDIT_AUTHOR_NOTE_URL)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, NoteForm)

    def test_reader_cannot_edit_author_note(self):
        """Тест невозможности редактирования записи другого пользователя"""
        response = self.client.get(self.EDIT_READER_NOTE_URL)
        self.assertIn(response.status_code, [302, 403, 404])
