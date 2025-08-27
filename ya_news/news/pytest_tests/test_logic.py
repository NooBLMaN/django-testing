import pytest
from django.urls import reverse
from http import HTTPStatus

from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    comment_data = {
        'text': 'Комментарий анонима'
    }

    response = client.post(url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    assert reverse('users:login') in response.url
    comment_count = Comment.objects.count()
    assert comment_count == 0


@pytest.mark.django_db
def test_autorized_user_can_create_comment(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    comment_data = {
        'text': 'Комментарий пользователя'
    }

    response = author_client.post(url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    comment_count = Comment.objects.count()
    assert comment_count == 1
    comment = Comment.objects.first()
    assert comment.text == comment_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {
        'text': 'Комментарий пользователя с плохим словом "редиска"'
    }
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert response.context['form'].errors
    comment_count = Comment.objects.count()
    assert comment_count == 0


@pytest.mark.django_db
def test_author_can_edit_own_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    edit_data = {
        'text': 'Новый текст'
    }
    response = author_client.post(url, data=edit_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    comment_count = Comment.objects.count()
    assert comment_count == 1
    assert comment.text == edit_data['text']


@pytest.mark.django_db
def test_author_can_delete_own_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    comment_count = Comment.objects.count()
    assert comment_count == 0


@pytest.mark.django_db
def test_author_cannot_edit_other_comment(other_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    original_text = comment.text
    edit_data = {
        'text': 'Новый текст'
    }
    response = other_client.post(url, data=edit_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    comment_count = Comment.objects.count()
    assert comment_count == 1
    assert comment.text == original_text


@pytest.mark.django_db
def test_author_cannot_delete_other_comment(other_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = other_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_count = Comment.objects.count()
    assert comment_count == 1
