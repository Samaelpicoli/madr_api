from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database.get_session import get_session
from madr.models.account import Account
from madr.schemas.token_schema import Token
from madr.security.account_check import get_current_account
from madr.security.generate_token import create_access_token
from madr.security.password_check import verify_password

router = APIRouter(prefix='/auth', tags=['auth'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentAccount = Annotated[Account, Depends(get_current_account)]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2Form,
    session: T_Session,
):
    """
    Autentica uma conta de usuário e retorna um token de acesso.
    Esta função manipula requisições POST para a rota '/token'.
    Utiliza o formulário de autenticação OAuth2 para verificar as credenciais.

    Args:
        form_data (OAuth2PasswordRequestForm): O formulário contendo
        as credenciais do usuário.
        session (Session): A sessão do banco de dados.

    Returns:
        dict: Um dicionário contendo o token de acesso.

    Raises:
        HTTPException: Se as credenciais forem inválidas.
    """
    account = await session.scalar(
        select(Account).where(Account.email == form_data.username)
    )

    if not account:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, account.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    access_token = create_access_token({'sub': account.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post('/refresh/token', response_model=Token)
async def refresh_access_token(account: CurrentAccount):
    """
    Esta função manipula requisições POST para a rota '/refresh/token'.
    Retorna um novo token de acesso para o usuário autenticado.

    Args:
        account (CurrentAccount): O usuário autenticado atual, obtido
        através da dependência get_current_account.

    Returns:
        Token: Um objeto Token contendo o novo token de acesso.
    """
    access_token = create_access_token({'sub': account.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}
