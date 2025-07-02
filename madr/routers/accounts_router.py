from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database.get_session import get_session
from madr.models.account import Account
from madr.schemas.account_schema import (
    AccountList,
    AccountPublic,
    AccountSchema,
)
from madr.schemas.message_schema import Message
from madr.schemas.page_schema import FilterPage
from madr.security.account_check import get_current_account
from madr.security.password_check import get_password_hash

router = APIRouter(prefix='/accounts', tags=['accounts'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentAccount = Annotated[Account, Depends(get_current_account)]


@router.get('/', status_code=HTTPStatus.OK, response_model=AccountList)
async def read_accounts(
    session: T_Session,
    current_account: CurrentAccount,
    filter_accounts: Annotated[FilterPage, Query()],
):
    """
    Retorna uma lista de contas de usuários.
    Esta função manipula requisições GET para a rota '/accounts/'.
    Retorna uma lista de contas com base nos parâmetros de
    paginação 'skip' e 'limit'.
    Somente usuários com login poderão acessar esta rota.

    Args:
        session (Session): A sessão do banco de dados.
        current_account (Account): O usuário autenticado atual.
        filter_accounts (FilterPage): Parâmetros de paginação para filtrar
        as contas, incluindo 'skip' e 'limit'.

    Returns:
        AccountList: Uma lista de contas com nome e email.
    """
    accounts = await session.scalars(
        select(Account)
        .offset(filter_accounts.offset)
        .limit(filter_accounts.limit)
    )
    accounts = accounts.all()
    return {'accounts': accounts}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AccountPublic)
async def create_account(account: AccountSchema, session: T_Session):
    """
    Cria uma nova conta de usuário.
    Esta função manipula requisições POST para a rota '/accounts/'.
    Retorna os dados da conta de usuário criado.

    Args:
        account (AccountSchema): Os dados da conta de usuário a serem criados.
        session (Session): A sessão do banco de dados.

    Returns:
        AccountPublic: Os dados do usuário criado.

    Raises:
        HTTPException: Se o nome de usuário ou e-mail já existirem.
    """
    db_account = await session.scalar(
        select(Account).where(
            (Account.username == account.username)
            | (Account.email == account.email)
        )
    )

    if db_account:
        if db_account.username == account.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        if db_account.email == account.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

    db_account = Account(
        username=account.username,
        password=get_password_hash(account.password),
        email=account.email,
    )
    session.add(db_account)
    await session.commit()
    await session.refresh(db_account)

    return db_account


@router.put(
    '/{account_id}', status_code=HTTPStatus.OK, response_model=AccountPublic
)
async def update_account(
    account_id: int,
    account: AccountSchema,
    session: T_Session,
    current_account: CurrentAccount,
):
    """
    Atualiza os dados de uma conta de usuário.
    Permite que um usuário autenticado atualize sua própria conta.
    O usuário só pode atualizar sua própria conta, não podendo
    atualizar outros contas do sistema.

    Args:
        account_id (int): ID do usuário a ser atualizado.
        account (AccountSchema): Dados da conta a serem atualizados.
        session (Session): Sessão do banco de dados.
        current_account (Account): Conta de usuário autenticado atual.

    Returns:
        AccountPublic: Os dados atualizados da conta do usuário.

    Raises:
        HTTPException: Se tentar atualizar outro usuário do banco ou se o
        nome de usuário ou e-mail já existirem.
    """
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    try:
        current_account.email = account.email
        current_account.username = account.username
        current_account.password = get_password_hash(account.password)

        session.add(current_account)
        await session.commit()
        await session.refresh(current_account)

        return current_account

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@router.delete(
    '/{account_id}', status_code=HTTPStatus.OK, response_model=Message
)
async def delete_account(
    account_id: int,
    session: T_Session,
    current_account: CurrentAccount,
):
    """
    Remove uma conta de usuário do sistema.
    Permite que um usuário autenticado remova sua própria conta.
    O usuário só pode deletar sua própria conta, não podendo
    remover outros contas do sistema.

    Args:
        account_id (int): ID do usuário a ser removido.
        session (Session): Sessão do banco de dados.
        current_account (Account): Usuário autenticado atual.

    Returns:
        Message: Dicionário com mensagem de confirmação.

    Raises:
        HTTPException: Se tentar deletar outro usuário do banco.
    """
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    await session.delete(current_account)
    await session.commit()

    return {'message': 'Account deleted successfully'}


@router.get('/{account_id}', response_model=AccountPublic)
async def get_account(account_id: int, session: T_Session):
    """
    Retorna os dados de uma conta de usuário específico.
    Esta função manipula requisições GET para a rota '/accounts/{account_id}'.
    Retorna os dados da conta do usuário correspondente ao ID fornecido.

    Args:
        account_id (int): O ID do usuário a ser retornado.
        session (Session): A sessão do banco de dados.

    Returns:
        AccountPublic: Os dados da conta do usuário.
    """
    account_db = await session.scalar(
        select(Account).where(Account.id == account_id)
    )
    if not account_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Account not found'
        )

    return account_db
