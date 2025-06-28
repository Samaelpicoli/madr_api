from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.models.author import Author


def test_create_author(session: Session, mock_db_time):
    with mock_db_time(model=Author) as time:
        new_account = Author(
            name='Machado de Assis',
        )
        session.add(new_account)
        session.commit()
        account = session.scalar(
            select(Author).where(Author.name == 'Machado de Assis')
        )
    assert asdict(account) == {
        'id': 1,
        'name': 'Machado de Assis',
        'books': [],
        'created_at': time,
        'updated_at': time,
    }
