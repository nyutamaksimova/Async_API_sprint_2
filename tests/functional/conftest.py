import uuid

import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='es_client')
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_settings.es_host, verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='movies_data')
async def movies_data():
    es_data = [{
        'uuid': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': [{
            "uuid": '13f92c28-baf8-437b-94bb-d891bd835656',
            "name": "Action"
        },
            {
                "uuid": '13f86c28-baf8-437b-94bb-d891bd835656',
                "name": "Sci-Fi"
            }],
        'title': 'The Star',
        'description': 'New World',
        'directors_names': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'uuid': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'full_name': 'Ann'},
            {'uuid': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'full_name': 'Bob'}
        ],
        'writers': [
            {'uuid': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'full_name': 'Ben'},
            {'uuid': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'Howard'}
        ],
        'directors': [
            {'uuid': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'full_name': 'Stan'}
        ]
    } for _ in range(60)]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': 'movies', '_id': row['uuid']}
        data.update({'_source': row})
        bulk_query.append(data)

    return bulk_query


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client):
    async def inner(data: list[dict]):

        if await es_client.indices.exists(index=test_settings.es_index):
            await es_client.indices.delete(index=test_settings.es_index)
        await es_client.indices.create(index=test_settings.es_index, **test_settings.es_index_mapping)

        updated, errors = await async_bulk(client=es_client, actions=data)

        await es_client.indices.refresh(index=test_settings.es_index)

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture(name='make_get_request')
def make_get_request(es_client):
    async def inner(url: str, query_data):
        url = test_settings.service_url + url

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=query_data) as response:
                body = await response.json()
                headers = response.headers
                status = response.status
        return status, body

    return inner
