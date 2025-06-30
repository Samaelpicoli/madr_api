from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.models.author import Author
from madr.models.book import Book


def test_create_book(session: Session, mock_db_time):
    new_account = Author(
        name='Machado de Assis',
    )
    session.add(new_account)
    session.commit()
    account = session.scalar(
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
        session.commit()
        print(new_book)
        book = session.scalar(
            select(Book).where(Book.title == 'Memórias Póstumas de Brás Cubas')
        )
    assert book.id == 1
    assert book.author_id == 1
    assert book.author.name == 'Machado de Assis'
    assert book.author.books == [book]
    assert book.title == 'Memórias Póstumas de Brás Cubas'
    assert book.year == year_created
