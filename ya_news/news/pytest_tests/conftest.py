import pytest
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse

from news.models import News, Comment
from yanews.settings import BAD_WORDS, NEWS_COUNT_ON_HOME_PAGE

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
    comment_list = []
    today = datetime.today()
    yesterday = today - timedelta(days=1)

    for i in range(NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
            created=yesterday if i % 2 == 0 else today
        )
        comment_list.append(comment)
    return comment_list


@pytest.fixture
def bad_words_data():
    bad_words_data = {
        'text': f'Комментарий пользователя с плохим словом {BAD_WORDS[0]}'
    }
    return bad_words_data


@pytest.fixture
def comment_data():
    comment_data = {
        'text': 'Комментарий'
    }
    return comment_data


@pytest.fixture
def edit_data():
    edit_data = {
        'text': 'Новый текст'
    }
    return edit_data


@pytest.fixture
def news_detail_url(news):
    return reverse(DETAIL_URL, args=(news.id,))


@pytest.fixture
def order_news():
    news_list = []
    today = datetime.today()
    yesterday = today - timedelta(days=1)

    for i in range(10):
        news = News.objects.create(
            title=f'Новость {i}',
            text=f'текст {i}',
            date=yesterday if i % 2 == 0 else today
        )
        news_list.append(news)
    return news_list


@pytest.fixture
def edit_comment_url(comment):
    return reverse(EDIT_URL, args=(comment.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse(DELETE_URL, args=(comment.id,))
