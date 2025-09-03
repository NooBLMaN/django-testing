from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


COMMON_PAGES = [
    (lf('home_url'), 'get', HTTPStatus.OK),
    (lf('news_detail_url'), 'get', HTTPStatus.OK),
    (lf('login_url'), 'get', HTTPStatus.OK),
    (lf('signup_url'), 'get', HTTPStatus.OK),
]

COMMENT_ACTIONS = [
    (lf('edit_comment_url'), 'get'),
    (lf('delete_comment_url'), 'get'),
]


@pytest.mark.parametrize("url,method,expected", COMMON_PAGES)
def test_common_pages_status(client, url, method, expected):
    """Тест статус-кодов основных страниц для любого пользователя."""
    response = getattr(client, method)(url)
    assert response.status_code == expected


@pytest.mark.parametrize("url,method", COMMENT_ACTIONS)
def test_comment_action_status_author(author_client, url, method):
    """Тест доступа автора к редактированию и удалению комментария."""
    response = getattr(author_client, method)(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("url,method", COMMENT_ACTIONS)
def test_comment_action_status_not_author(other_client, url, method):
    """Тест отказа в доступе не-автору к редактированию и
    удалению комментария.
    """
    response = getattr(other_client, method)(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("url,method", COMMENT_ACTIONS)
def test_comment_action_redirect_anonymous(client, login_url, url, method):
    """Тест редиректа анонимного пользователя."""
    expected_redirect = f"{login_url}?next={url}"
    response = getattr(client, method)(url)
    assertRedirects(response, expected_redirect)
