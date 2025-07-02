from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.models.author import Author


@pytest.mark.asyncio
async def test_create_author(session: AsyncSession, mock_db_time):
    with mock_db_time(model=Author) as time:
        new_account = Author(
            name='Machado de Assis',
        )
        session.add(new_account)
        await session.commit()
        account = await session.scalar(
            select(Author).where(Author.name == 'Machado de Assis')
        )
    assert asdict(account) == {
        'id': 1,
        'name': 'Machado de Assis',
        'books': [],
        'created_at': time,
        'updated_at': time,
    }
