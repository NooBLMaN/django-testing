from notes.forms import NoteForm
from notes.tests.conftest import BaseNoteList


class TestAuthorNoteList(BaseNoteList):

    def test_note_in_list_for_author(self):
        """Тест проверки, что заметка автора присутствует в списке заметок"""
        response = self.client.get(self.LIST_URL)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])
        self.assertNotIn(self.another_note, response.context['object_list'])
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

    def test_create_and_edit_note_page_contains_form(self):
        """Тест, что страница создания имеет форму"""
        url_list = [self.ADD_URL, self.EDIT_AUTHOR_NOTE_URL]

        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
