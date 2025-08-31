import pytest

from datetime import datetime, timedelta

from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from news.models import News, Comment

User = get_user_model()

HOME_URL = reverse('news:home')
LOGIN_URL = reverse('users:login')
SIGNUP_URL = reverse('users:signup')
DETAIL_URL = 'news:detail'
EDIT_URL = 'news:edit'
DELETE_URL = 'news:delete'


@pytest.fixture
def login_url():
    return LOGIN_URL


@pytest.fixture
def home_url():
    return HOME_URL


@pytest.fixture
def signup_url():
    return SIGNUP_URL


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


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
def news(db):
    return News.objects.create(
        title='Тестовая новость',
        text='Тестовая новость',
    )


@pytest.fixture
def comment(news, author):
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


@pytest.fixture
def news_on_home_page():
    news_list = []
    for i in range(15):
        news = News.objects.create(
            title=f'Новость {i}',
            text=f'Текст{i}'
        )
        news_list.append(news)
    return news_list


@pytest.fixture
def comments(news, author):
    today = datetime.today()

    yesterday = today - timedelta(days=1)

    comment1 = Comment.objects.create(
        news=news,
        author=author,
        text='Старый комментарий',
        created=yesterday
    )
    comment2 = Comment.objects.create(
        news=news,
        author=author,
        text='Новый комментарий',
        created=today
    )
    return [comment1, comment2]


@pytest.fixture
def news_detail_url(news):
    return reverse(DETAIL_URL, args=(news.id,))


@pytest.fixture
def order_news():
    today = datetime.today()

    yesterday = today - timedelta(days=1)

    news1 = News.objects.create(
        title='Старая новость',
        text='Старый текст',
        date=yesterday,
    )
    news2 = News.objects.create(
        title='Новая новость',
        text='Новый текст',
        date=today,
    )
    return [news1, news2]


@pytest.fixture
def edit_comment_url(comment):
    return reverse(EDIT_URL, args=(comment.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse(DELETE_URL, args=(comment.id,))
