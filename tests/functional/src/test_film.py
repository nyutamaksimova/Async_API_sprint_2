import pytest


@pytest.mark.asyncio
async def test_films_page_size_less_than_min(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films',
        {
            'page_size': 0,
        }
    )

    assert status == 422


@pytest.mark.asyncio
async def test_films_page_size_more_than_max(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films',
        {
            'page_size': 101,
        }
    )

    assert status == 422


@pytest.mark.asyncio
async def test_films_page_number_less_than_min(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films',
        {
            'page_number': 0,
        }
    )

    assert status == 422


@pytest.mark.asyncio
async def test_films_invalid_sort_field(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films',
        {
            'sort': 'aaaaa',
        }
    )

    assert status == 400


@pytest.mark.asyncio
async def test_films_list(es_write_data, make_get_request, movies_data):
    await es_write_data(movies_data)

    status, body = await make_get_request('/api/v1/films', {})

    assert status == 200
    assert len(body) == 50


@pytest.mark.asyncio
async def test_films_page_size(movies_data, es_write_data, make_get_request):
    await es_write_data(movies_data)

    status, body = await make_get_request(
        '/api/v1/films',
        {
            'page_size': 10,
        }
    )

    assert status == 200
    assert len(body) == 10


@pytest.mark.asyncio
async def test_films_pagination(movies_data, es_write_data, make_get_request):
    await es_write_data(movies_data)

    status, page1 = await make_get_request(
        '/api/v1/films',
        {'page_size': 10, 'page_number': 1}
    )

    status, page2 = await make_get_request(
        '/api/v1/films',
        {'page_size': 10, 'page_number': 2}
    )

    assert status == 200
    assert page1 != page2
    assert len(page1) == 10
    assert len(page2) == 10


@pytest.mark.asyncio
async def test_film_by_id(es_write_data, make_get_request, movies_data):
    await es_write_data(movies_data)

    film_id = movies_data[0]['_source']['uuid']

    status, body = await make_get_request(f'/api/v1/films/{film_id}', {})

    assert status == 200
    assert body['uuid'] == film_id


@pytest.mark.asyncio
async def test_film_by_id_not_found(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films/00000000-0000-0000-0000-000000000000',
        {}
    )

    assert status == 404


@pytest.mark.asyncio
async def test_similar_films(es_write_data, make_get_request, movies_data):
    await es_write_data(movies_data)

    film_id = movies_data[0]['_source']['uuid']

    status, body = await make_get_request(
        f'/api/v1/films/{film_id}/similar',
        {}
    )

    assert status == 200
    assert isinstance(body, list)


@pytest.mark.asyncio
async def test_similar_films_not_found(make_get_request):
    status, _ = await make_get_request(
        '/api/v1/films/00000000-0000-0000-0000-000000000000/similar',
        {}
    )

    assert status == 404


@pytest.mark.asyncio
async def test_films_cache(movies_data, es_client, es_write_data, make_get_request, ):
    await es_write_data(movies_data)

    film_id = movies_data[0]['_source']['uuid']

    status, body1 = await make_get_request(
        f'/api/v1/films/{film_id}', {})

    assert status == 200

    await es_client.indices.delete(index='movies')

    status, body2 = await make_get_request(
        f'/api/v1/films/{film_id}', {})

    assert status == 200
    assert body1 == body2
