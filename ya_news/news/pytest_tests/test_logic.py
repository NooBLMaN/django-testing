from http import HTTPStatus

from news.models import Comment

from yanews.settings import BAD_WORDS


def test_anonymous_user_cant_create_comment(client, news, news_detail_url,
                                            login_url):
    """Тест невозможности отправки комментария не
    авторизованному пользователю
    """
    comment_data = {
        'text': 'Комментарий анонима'
    }

    initial_count = Comment.objects.count()

    response = client.post(news_detail_url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    assert login_url in response.url
    comment_count = Comment.objects.count()
    assert comment_count == initial_count


def test_autorized_user_can_create_comment(author_client, news,
                                           news_detail_url, author):
    """Тест возможности отправки комментария
    авторизованному пользователю
    """
    comment_data = {
        'text': 'Комментарий пользователя'
    }

    initial_count = Comment.objects.count()

    response = author_client.post(news_detail_url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    final_count = Comment.objects.count()
    assert final_count == initial_count + 1
    comment = Comment.objects.first()
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, news_detail_url):
    """Тест невозможности отправки комментария с плохим словом"""
    bad_words_data = {
        'text': f'Комментарий пользователя с плохим словом {BAD_WORDS[0]}'
    }

    comment_count_before = Comment.objects.count()

    response = author_client.post(news_detail_url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert response.context['form'].errors
    comment_count = Comment.objects.count()
    assert comment_count == comment_count_before


def test_author_can_edit_own_comment(author_client, comment, edit_comment_url):
    """Тест возможности редактировать собственный комментарий
    авторизованному пользователю
    """
    edit_data = {
        'text': 'Новый текст'
    }

    original_data = {
        'id': comment.id,
        'text': comment.text,
        'news_id': comment.news_id,
        'author_id': comment.author_id,
        'created': comment.created
    }

    comment_before = list(Comment.objects.values('id', 'text', 'news_id',
                                                 'author_id', 'created'))

    response = author_client.post(edit_comment_url, data=edit_data)
    assert response.status_code == HTTPStatus.FOUND
    comment_after = list(Comment.objects.values('id', 'text', 'news_id',
                                                'author_id', 'created'))
    assert len(comment_after) == len(comment_before)
    edited_comment = Comment.objects.get(id=comment.id,)
    assert edited_comment.text == edit_data['text']
    assert edited_comment.text != original_data['text']
    assert edited_comment.news_id == original_data['news_id']
    assert edited_comment.author_id == original_data['author_id']


def test_author_can_delete_own_comment(author_client, comment,
                                       delete_comment_url):
    """Тест возможности удалить собственный комментарий
    авторизованному пользователю
    """
    response = author_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.FOUND
    comment_count = Comment.objects.count()
    assert comment_count == 0


def test_author_cannot_edit_other_comment(other_client, comment,
                                          edit_comment_url):
    """Тест невозможности отредактировать чужой комментарий"""
    edit_data = {
        'text': 'Новый текст'
    }

    original_data = {
        'id': comment.id,
        'text': comment.text,
        'news_id': comment.news_id,
        'author_id': comment.author_id,
        'created': comment.created
    }

    comment_before = list(Comment.objects.values('id', 'text', 'news_id',
                                                 'author_id', 'created'))

    response = other_client.post(edit_comment_url, data=edit_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_after = list(Comment.objects.values('id', 'text', 'news_id',
                                                'author_id', 'created'))
    assert comment_after == comment_before
    comment.refresh_from_db()
    assert comment.text == original_data['text']
    assert comment.news_id == original_data['news_id']
    assert comment.author_id == original_data['author_id']
    assert comment.created == original_data['created']


def test_author_cannot_delete_other_comment(other_client, comment,
                                            delete_comment_url):
    """Тест невозможности удалить чужой комментарий"""
    response = other_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_count = Comment.objects.count()
    assert comment_count == 1
