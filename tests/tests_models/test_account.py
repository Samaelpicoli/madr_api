from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.models.account import Account


@pytest.mark.asyncio
async def test_create_account(session: AsyncSession, mock_db_time):
    """
    Testa a criação de uma conta de usuário no banco de dados.
    Verifica se o usuário é criado corretamente com os dados fornecidos
    e se o campo 'created_at' e 'updated_at' é definido corretamente.
    """
    with mock_db_time(model=Account) as time:
        new_account = Account(
            username='testuser',
            email='teste@teste.com',
            password='testpassword',
        )
        session.add(new_account)
        await session.commit()

        account = await session.scalar(
            select(Account).where(Account.username == 'testuser')
        )

    assert asdict(account) == {
        'id': 1,
        'username': 'testuser',
        'email': 'teste@teste.com',
        'password': 'testpassword',
        'created_at': time,
        'updated_at': time,
    }
