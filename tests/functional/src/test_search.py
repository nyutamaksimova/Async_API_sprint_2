import pytest


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'The Star'},
                {'status': 200, 'length': 50}
        ),
        (
                {'query': 'Mashed potato'},
                {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(movies_data, es_write_data, make_get_request, query_data, expected_answer):
    await es_write_data(movies_data)

    status, body = await make_get_request('/api/v1/films/search', query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']


@pytest.mark.asyncio
async def test_search_without_query(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films/search',
        {}
    )

    assert status == 422


@pytest.mark.asyncio
async def test_search_empty_query(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films/search',
        {'query': ''}
    )

    assert status == 422


@pytest.mark.asyncio
async def test_search_page_size_less_than_min(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_size': 0,
        }
    )

    assert status == 422


@pytest.mark.asyncio
async def test_search_page_size_more_than_max(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_size': 101,
        }
    )

    assert status == 422


@pytest.mark.asyncio
async def test_search_page_number_less_than_min(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_number': 0,
        }
    )

    assert status == 422


@pytest.mark.asyncio
async def test_search_page_size(movies_data, es_write_data, make_get_request):
    await es_write_data(movies_data)

    status, body = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_size': 10,
        }
    )

    assert status == 200
    assert len(body) == 10


@pytest.mark.asyncio
async def test_search_pagination(movies_data, es_write_data, make_get_request):
    await es_write_data(movies_data)

    status, body = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_size': 10,
            'page_number': 2,
        }
    )

    assert status == 200
    assert len(body) == 10


@pytest.mark.asyncio
async def test_search_cache(movies_data, es_client, es_write_data, make_get_request, ):
    await es_write_data(movies_data)

    query = {'query': 'The Star'}

    status, body = await make_get_request(
        '/api/v1/films/search',
        query,
    )

    assert status == 200
    assert len(body) == 50

    await es_client.indices.delete(index='movies')

    status, body = await make_get_request(
        '/api/v1/films/search',
        query,
    )

    assert status == 200
    assert len(body) == 50
