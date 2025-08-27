import pytest
from django.test.client import Client
from django.contrib.auth import get_user_model
from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create(username='Тестовый пользователь')


@pytest.fixture
def other_user(db):
    return User.objects.create(username='Другой пользователь')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news(db, author):
    return News.objects.create(
        title='Тестовая новость',
        text='Тестовая новость',
    )


@pytest.fixture
def comment(db, news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def other_client(other_user):
    client = Client()
    client.force_login(other_user)
    return client
