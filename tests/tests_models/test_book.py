import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.models.author import Author
from madr.models.book import Book


@pytest.mark.asyncio
async def test_create_book(session: AsyncSession, mock_db_time):
    new_account = Author(
        name='Machado de Assis',
    )
    session.add(new_account)
    await session.commit()
    account = await session.scalar(
        select(Author).where(Author.name == 'Machado de Assis')
    )
    with mock_db_time(model=Author) as _:
        year_created = 1881
        new_book = Book(
            title='Memórias Póstumas de Brás Cubas',
            year=year_created,
            author_id=account.id,
        )
        session.add(new_book)
        await session.commit()
        book = await session.scalar(
            select(Book).where(Book.title == 'Memórias Póstumas de Brás Cubas')
        )
    assert book.id == 1
    assert book.author_id == 1
    assert book.author.name == 'Machado de Assis'
    assert book.title == 'Memórias Póstumas de Brás Cubas'
    assert book.year == year_created
