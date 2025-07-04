from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database.get_session import get_session
from madr.models.account import Account
from madr.models.author import Author
from madr.models.book import Book
from madr.schemas.book_schema import (
    BookList,
    BookPublic,
    BookSchema,
    BookUpdate,
    FilterBook,
)
from madr.schemas.message_schema import Message
from madr.security.account_check import get_current_account

router = APIRouter(prefix='/books', tags=['books'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentAccount = Annotated[Account, Depends(get_current_account)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=BookPublic)
async def create_book(
    book: BookSchema, session: T_Session, account: CurrentAccount
):
    """
    Esta função manipula requisições POST para a rota '/books/'.
    Cria um novo livro com base nos dados fornecidos no corpo da requisição.

    Args:
        book (BookSchema): Dados do livro a ser criado.
        session (Session): A sessão do banco de dados.
        account (CurrentAccount): O usuário autenticado atual.

    Returns:
        BookPublic: O livro criado com os campos públicos.

    Raises:
        HTTPException: Se o título do livro já existir no banco de dados.
    """
    author = await session.get(Author, book.author_id)
    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Author not found',
        )
    book_db = await session.scalar(
        select(Book).where(func.lower(Book.title) == book.title.lower())
    )
    if book_db:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Book already exists',
        )
    new_book = Book(title=book.title, year=book.year, author_id=book.author_id)
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)
    return new_book


@router.delete('/{book_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_book(
    book_id: int, session: T_Session, account: CurrentAccount
):
    """
    Esta função manipula requisições DELETE para a rota '/books/{book_id}'.
    Deleta o livro com o ID fornecido.

    Args:
        book_id (int): O ID do livro a ser deletado.
        session (Session): A sessão do banco de dados.
        account (CurrentAccount): O usuário autenticado atual.

    Returns:
        Message: Mensagem de sucesso indicando que o livro foi deletado.

    Raises:
        HTTPException: Se o livro não for encontrado.
    """
    book = await session.scalar(select(Book).where(Book.id == book_id))
    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Book not found',
        )
    await session.delete(book)
    await session.commit()
    return {'message': 'Book deleted successfully'}


@router.patch('/{book_id}', response_model=BookPublic)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    session: T_Session,
    account: CurrentAccount,
):
    """
    Esta função manipula requisições PATCH para a rota '/books/{book_id}'.
    Atualiza o livro com o ID fornecido com os dados fornecidos
    no corpo da requisição.

    Args:
        book_id (int): O ID do livro a ser atualizado.
        book_data (BookUpdate): Dados do livro a serem atualizados.
        session (Session): A sessão do banco de dados.
        account (CurrentAccount): O usuário autenticado atual.

    Returns:
        BookPublic: O livro atualizado com os campos públicos.

    Raises:
        HTTPException: Se o livro não for encontrado ou se o título do
        livro já existir.
    """
    book = await session.scalar(select(Book).where(Book.id == book_id))
    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Book not found',
        )
    if book_data.title:
        existing_book = await session.scalar(
            select(Book).where(
                func.lower(Book.title) == book_data.title.lower()
            )
        )
        if existing_book and existing_book.id != book_id:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Book already exists',
            )
        book.title = book_data.title

    if book_data.year:
        book.year = book_data.year

    session.add(book)
    await session.commit()
    await session.refresh(book)

    return book


@router.get('/{book_id}', response_model=BookPublic, status_code=HTTPStatus.OK)
async def get_book(book_id: int, session: T_Session, account: CurrentAccount):
    """
    Esta função manipula requisições GET para a rota '/books/{book_id}'.
    Retorna os dados do livro correspondente ao ID fornecido.

    Args:
        book_id (int): O ID do livro a ser retornado.
        session (Session): A sessão do banco de dados.
        account (CurrentAccount): O usuário autenticado atual.

    Returns:
        BookPublic: Os dados do livro encontrado.

    Raises:
        HTTPException: Se o livro não for encontrado.
    """
    book = await session.scalar(select(Book).where(Book.id == book_id))
    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found'
        )
    return book


@router.get('/', response_model=BookList, status_code=HTTPStatus.OK)
async def get_books(
    session: T_Session,
    account: CurrentAccount,
    book_filter: Annotated[FilterBook, Query()],
):
    """
    Esta função manipula requisições GET para a rota '/books/'.
    Retorna uma lista de livros filtrados por título e ordenados por ID.

    Args:
        session (Session): A sessão do banco de dados.
        account (CurrentAccount): O usuário autenticado atual.
        book_filter (FilterBook): Filtros para busca de livros.

    Returns:
        BookList: Lista de livros filtrados e ordenados.

    Raises:
        HTTPException: Se ocorrer um erro ao consultar os livros.
    """
    query = select(Book).order_by(Book.id)
    if book_filter.title:
        query = query.where(Book.title.ilike(f'%{book_filter.title}%'))

    if book_filter.year:
        query = query.where(Book.year == book_filter.year)

    query = query.offset(book_filter.offset).limit(book_filter.limit)

    books = await session.scalars(query)
    books = books.all()
    return BookList(books=books)
