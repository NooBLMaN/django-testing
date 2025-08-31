from news.forms import CommentForm

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


def test_news_count_on_home_page(client, news_on_home_page, home_url):
    """Тест кол-ва новостей на глвной странице"""
    response = client.get(home_url)

    assert 'news_list' in response.context
    assert len(response.context['news_list']) <= NEWS_COUNT_ON_HOME_PAGE


def test_comment_order(client, news, comments, news_detail_url):
    """Тест сортировки комментариев в хронологическом порядке на
    странице отдельной новости
    """
    response = client.get(news_detail_url)

    assert 'news' in response.context
    news_obj = response.context['news']
    comments = news_obj.comment_set.all()

    assert len(comments) == 2
    assert comments[0].text == 'Старый комментарий'
    assert comments[1].text == 'Новый комментарий'


def test_news_order(client, order_news, home_url):
    """Тест сортировки новостей в хронологическом порядке на
    домашней странице
    """
    response = client.get(home_url)

    assert 'news_list' in response.context
    new_list = response.context['news_list']

    assert len(new_list) >= 2
    assert new_list[0].text == 'Новый текст'
    assert new_list[1].text == 'Старый текст'


def test_anonymous_client_has_no_form(client, news, news_detail_url):
    """Тест недоступности формы отправки комментария для
    анонимного пользователя
    """
    response = client.get(news_detail_url)

    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news, news_detail_url):
    """Тест доступности формы отправки комментария для
    авторизованного пользователя
    """
    response = author_client.get(news_detail_url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
