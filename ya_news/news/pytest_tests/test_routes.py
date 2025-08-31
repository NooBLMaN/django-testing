from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


COMMON_PAGES = [
    ("news:home", None, "get", HTTPStatus.OK),
    ("news:detail", "news", "get", HTTPStatus.OK),
    ("users:login", None, "get", HTTPStatus.OK),
    ("users:signup", None, "get", HTTPStatus.OK),
]

COMMENT_ACTIONS = [
    ("news:edit", "comment", "get"),
    ("news:delete", "comment", "get"),
]


def get_url(name, arg_name, request):
    """
    Генерирует URL по имени маршрута с аргументом из фикстуры,
    если он указан.
    """
    if not arg_name:
        return reverse(name)

    # Получаем объект фикстуры
    obj = request.getfixturevalue(arg_name)
    # Для новости и комментария используем id
    return reverse(name, args=(obj.id,))


@pytest.mark.django_db
@pytest.mark.parametrize("name,arg_name,method,expected", COMMON_PAGES)
def test_common_pages_status(request, client, name, arg_name,
                             method, expected):
    """Тест статус-кодов основных страниц для любого пользователя."""
    url = get_url(name, arg_name, request)
    response = getattr(client, method)(url)
    assert response.status_code == expected


@pytest.mark.django_db
@pytest.mark.parametrize("action,arg_name,method", COMMENT_ACTIONS)
def test_comment_action_status_author(request, author_client, action,
                                      arg_name, method):
    """Тест доступа автора к редактированию и удалению комментария."""
    url = get_url(action, arg_name, request)
    response = getattr(author_client, method)(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize("action,arg_name,method", COMMENT_ACTIONS)
def test_comment_action_status_not_author(request, other_client, action,
                                          arg_name, method):
    """
    Тест отказа в доступе не-автору
    к редактированию и удалению комментария.
    """
    url = get_url(action, arg_name, request)
    response = getattr(other_client, method)(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize("action,arg_name,method", COMMENT_ACTIONS)
def test_comment_action_redirect_anonymous(request, client, action,
                                           arg_name, method, login_url):
    """
    Тест редиректа анонимного пользователя
    со страниц действий с комментарием.
    """
    url = get_url(action, arg_name, request)
    expected_redirect = f"{login_url}?next={url}"
    response = getattr(client, method)(url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect)
