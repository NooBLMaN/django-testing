import pytest
from django.urls import reverse
from datetime import datetime, timedelta

from news.models import News, Comment


@pytest.mark.django_db
def test_news_count_on_home_page(client):
    for i in range(15):
        News.objects.create(
            title=f'Новость {i}',
            text=f'Текст{i}'
        )

        url = reverse('news:home')
        response = client.get(url)

        assert 'news_list' in response.context
        assert len(response.context['news_list']) <= 10


@pytest.mark.django_db
def test_comment_order(client, news, author):

    today = datetime.today()

    yesterday = today - timedelta(days=1)

    Comment.objects.create(
        news=news,
        author=author,
        text='Старый комментарий',
        created=yesterday
    )
    Comment.objects.create(
        news=news,
        author=author,
        text='Новый комментарий',
        created=today
    )

    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)

    assert 'news' in response.context
    news_obj = response.context['news']
    comments = news_obj.comment_set.all()

    assert len(comments) == 2
    assert comments[0].text == 'Старый комментарий'
    assert comments[1].text == 'Новый комментарий'


@pytest.mark.django_db
def test_news_order(client):

    today = datetime.today()

    yesterday = today - timedelta(days=1)

    News.objects.create(
        title='Старая новость',
        text='Старый текст',
        date=yesterday,
    )
    News.objects.create(
        title='Новая новость',
        text='Новый текст',
        date=today,
    )

    url = reverse('news:home')
    response = client.get(url)

    assert 'news_list' in response.context
    new_list = response.context['news_list']

    assert new_list[0].text == 'Новый текст'
    assert new_list[1].text == 'Старый текст'


@pytest.mark.django_db
def test_comment_anon(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)

    assert 'form' not in response.context


@pytest.mark.django_db
def test_comment_user(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)

    assert 'form' in response.context
