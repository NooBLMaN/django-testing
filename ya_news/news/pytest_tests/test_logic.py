from http import HTTPStatus

from news.models import Comment


def test_anonymous_user_cant_create_comment(client, news, news_detail_url,
                                            login_url, comment_data):
    """Тест невозможности отправки комментария не
    авторизованному пользователю
    """
    initial_count = Comment.objects.count()

    response = client.post(news_detail_url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    assert login_url in response.url
    comment_count = Comment.objects.count()
    assert comment_count == initial_count


def test_user_can_create_comment(author_client, news, news_detail_url,
                                 author, comment_data):
    """Тест возможности отправки комментария
    авторизованному пользователю
    """
    initial_count = Comment.objects.count()

    response = author_client.post(news_detail_url, data=comment_data)
    assert response.status_code == HTTPStatus.FOUND
    final_count = Comment.objects.count()
    assert final_count == initial_count + 1
    comment = Comment.objects.first()
    assert comment.text == comment_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, news_detail_url,
                                 bad_words_data):
    """Тест невозможности отправки комментария с плохим словом"""
    comment_count_before = Comment.objects.count()

    response = author_client.post(news_detail_url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert response.context['form'].errors
    comment_count = Comment.objects.count()
    assert comment_count == comment_count_before


def test_author_can_edit_own_comment(author_client, comment, edit_comment_url,
                                     edit_data):
    """Тест возможности редактировать собственный комментарий
    авторизованному пользователю
    """
    original_text = comment.text
    initial_count = Comment.objects.count()

    response = author_client.post(edit_comment_url, data=edit_data)
    assert response.status_code == HTTPStatus.FOUND

    updated_comment = Comment.objects.get(id=comment.id)
    final_count = Comment.objects.count()

    assert final_count == initial_count
    assert updated_comment.text == edit_data['text']
    assert updated_comment.text != original_text


def test_author_can_delete_own_comment(author_client, comment,
                                       delete_comment_url):
    """Тест возможности удалить собственный комментарий
    авторизованному пользователю
    """
    initial_count = Comment.objects.count()
    response = author_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.FOUND

    final_count = Comment.objects.count()
    assert final_count == initial_count - 1
    assert not Comment.objects.filter(id=comment.id).exists()


def test_author_cannot_edit_other_comment(other_client, comment,
                                          edit_comment_url, edit_data):
    """Тест невозможности отредактировать чужой комментарий"""
    original_text = comment.text
    initial_count = Comment.objects.count()

    response = other_client.post(edit_comment_url, data=edit_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    unchanged_comment = Comment.objects.get(id=comment.id)
    final_count = Comment.objects.count()

    assert final_count == initial_count
    assert unchanged_comment.text == original_text


def test_author_cannot_delete_other_comment(other_client, comment,
                                            delete_comment_url):
    """Тест невозможности удалить чужой комментарий"""
    initial_count = Comment.objects.count()
    response = other_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    final_count = Comment.objects.count()
    assert final_count == initial_count
    assert Comment.objects.filter(id=comment.id).exists()
