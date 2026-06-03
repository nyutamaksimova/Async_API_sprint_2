from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.v1.schemes import FilmShort, Film
from src.core.messages import FILM_NOT_FOUND, INVALID_SORT_FIELD
from src.services.film import FilmService, get_film_service, InvalidSortFieldError

router = APIRouter()


@router.get(
    '',
    response_model=list[FilmShort],
    summary='Перечень фильмов',
    description='Перечень фильмов',
    response_description='Список фильмов'
)
async def films_list(
        sort: str = Query(default='-imdb_rating'),
        page_size: Annotated[int, Query(description='Количество элементов на странице', ge=1, le=100)] = 50,
        page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 1,
        film_service: FilmService = Depends(get_film_service),
):
    """Общий список фильмов"""
    try:
        films = await film_service.get_list(
            sort=sort,
            page_size=page_size,
            page_number=page_number,
        )
    except InvalidSortFieldError:
        raise HTTPException(
            status_code=400,
            detail=INVALID_SORT_FIELD,
        )
    return [FilmShort.model_validate(film) for film in films]


@router.get(
    '/search',
    response_model=list[FilmShort],
    summary='Поиск фильмов',
    description='Поиск фильмов по ключевым словам',
    response_description='Список подходящих фильмов'
)
async def film_search(
        query: str = Query(..., min_length=1),
        page_size: Annotated[int, Query(description='Количество элементов на странице', ge=1, le=100)] = 50,
        page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 1,
        film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    """Поиск по фильмам"""
    return await film_service.search(
        query=query,
        page_size=page_size,
        page_number=page_number,
    )


@router.get('/{film_id:uuid}',
            response_model=Film,
            summary="Информация о фильме",
            description="Вывод информации о конкретном фильме",
            response_description="Информация о фильме")
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> Film:
    """Информация об одном фильме"""
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)

    return Film.model_validate(film)


@router.get(
    '/{film_id:uuid}/similar',
    response_model=list[FilmShort],
    summary='Похожие фильмы',
    description='Поиск фильмов того же жанра',
    response_description='Список похожих фильмов'
)
async def similar_films(
        film_id: UUID,
        page_size: Annotated[int, Query(description='Количество элементов на странице', ge=1, le=100)] = 50,
        page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 1,
        film_service: FilmService = Depends(get_film_service),
):
    """Похожие по жанру"""
    films = await film_service.get_similar(
        film_id=film_id,
        page_size=page_size,
        page_number=page_number,
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)
    return films
