from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


# В файле conftest.py исправляем BaseNoteList
class BaseNoteList(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author')
        cls.reader = User.objects.create_user(username='reader')

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
        cls.EDIT_AUTHOR_NOTE_URL = reverse('notes:edit',
                                           args=[cls.note.slug])
        cls.EDIT_READER_NOTE_URL = reverse('notes:edit',
                                           args=[cls.another_note.slug])
        cls.DELETE_AUTHOR_NOTE_URL = reverse('notes:delete',
                                             args=[cls.note.slug])
        cls.DELETE_READER_NOTE_URL = reverse('notes:delete',
                                             args=[cls.another_note.slug])

        # Общие данные для формы
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст заметки',
            'slug': 'new-note-slug'
        }

    def setUp(self):
        # Авторизуем автора перед каждым тестом
        self.client.force_login(self.author)
