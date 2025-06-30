from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.database.get_session import get_session
from madr.models.account import Account
from madr.models.author import Author
from madr.schemas.author_schema import (
    AuthorList,
    AuthorPublic,
    AuthorSchema,
    AuthorUpdate,
    FilterAuthor,
)
from madr.schemas.message_schema import Message
from madr.security.account_check import get_current_account

router = APIRouter(prefix='/authors', tags=['authors'])

T_Session = Annotated[Session, Depends(get_session)]
CurrentAccount = Annotated[Account, Depends(get_current_account)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AuthorPublic)
def create_author(
    author: AuthorSchema, session: T_Session, account: CurrentAccount
):
    """
    Cria um novo autor.
    Esta função manipula requisições POST para a rota '/authors/'.
    Cria um novo autor com base nos dados fornecidos no corpo da requisição.

    Args:
        author (AuthorSchema): Dados do autor a ser criado.
        session (Session): A sessão do banco de dados.

    Returns:
        AuthorPublic: O autor criado com os campos públicos.

    Raises:
        HTTPException: Se o nome do autor já existir no banco de dados.
    """
    author_db = session.scalar(
        select(Author).where(Author.name == author.name)
    )
    if author_db:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Author already exists',
        )
    new_author = Author(name=author.name)
    session.add(new_author)
    session.commit()
    session.refresh(new_author)
    return new_author


@router.delete(
    '/{author_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_author(author_id: int, session: T_Session, account: CurrentAccount):
    """
    Deleta um autor pelo ID.
    Esta função manipula requisições DELETE para a rota '/authors/{author_id}'.
    Deleta o autor com o ID fornecido.

    Args:
        author_id (int): O ID do autor a ser deletado.
        session (Session): A sessão do banco de dados.

    Returns:
        Message: Mensagem de sucesso indicando que o autor foi deletado.

    Raises:
        HTTPException: Se o autor não for encontrado.
    """
    author = session.scalar(select(Author).where(Author.id == author_id))
    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Author not found',
        )
    session.delete(author)
    session.commit()
    return {'message': 'Author deleted successfully'}


@router.patch('/{author_id}', response_model=AuthorPublic)
def update_author(
    author_id: int,
    author_data: AuthorUpdate,
    session: T_Session,
    account: CurrentAccount,
):
    author = session.scalar(select(Author).where(Author.id == author_id))
    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Author not found',
        )
    if author_data.name:
        existing_author = session.scalar(
            select(Author).where(Author.name == author_data.name)
        )
        if existing_author and existing_author.id != author_id:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Author already exists',
            )
        author.name = author_data.name

    session.add(author)
    session.commit()
    session.refresh(author)

    return author


@router.get(
    '/{author_id}', response_model=AuthorPublic, status_code=HTTPStatus.OK
)
def get_author(author_id: int, session: T_Session, account: CurrentAccount):
    """
    Obtém os dados de um autor pelo ID.
    Esta função manipula requisições GET para a rota '/authors/{author_id}'.
    Retorna os dados do autor correspondente ao ID fornecido.

    Args:
        author_id (int): O ID do autor a ser retornado.
        session (Session): A sessão do banco de dados.

    Returns:
        AuthorPublic: Os dados do autor encontrado.

    Raises:
        HTTPException: Se o autor não for encontrado.
    """
    author = session.scalar(select(Author).where(Author.id == author_id))
    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )
    return author


@router.get('/', response_model=AuthorList, status_code=HTTPStatus.OK)
def get_authors(
    session: T_Session,
    account: CurrentAccount,
    author_filter: Annotated[FilterAuthor, Query()],
):
    """
    Obtém uma lista de autores com base nos filtros fornecidos.
    Esta função manipula requisições GET para a rota '/authors/'.
    Retorna uma lista de autores filtrados por nome e ordenados por ID.

    Args:
        session (Session): A sessão do banco de dados.
        account (CurrentAccount): O usuário autenticado atual.
        author_filter (FilterAuthor): Filtros para busca de autores.

    Returns:
        AuthorList: Lista de autores filtrados e ordenados.

    Raises:
        HTTPException: Se ocorrer um erro ao consultar os autores.
    """
    query = select(Author).order_by(Author.id)
    if author_filter.name:
        query = query.where(Author.name.ilike(f'%{author_filter.name}%'))

    query = query.offset(author_filter.offset).limit(author_filter.limit)

    authors = session.scalars(query).all()
    return AuthorList(authors=authors)
