from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database.get_session import get_session
from madr.models.account import Account
from madr.settings.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
settings = Settings()


async def get_current_account(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> Account:
    """
    Obtém e valida a conta do usuário atual através do token JWT.
    Verifica a validade do token JWT fornecido e retorna o usuário
    correspondente do banco de dados. Esta função é usada como uma
    dependência para endpoints que requerem autenticação.

    Args:
        session (Session): Sessão do banco de dados.
        token (str): Token JWT de autenticação, obtido do header Authorization.

    Returns:
        Account: Objeto de conta do usuário autenticado.

    Raises:
        HTTPException: Se o token for inválido, o email não existir ou o
        usuário não for encontrado no banco, erro 401 (Unauthorized).
    """
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    except ExpiredSignatureError:
        raise credentials_exception

    account = await session.scalar(
        select(Account).where(Account.email == subject_email)
    )

    if not account:
        raise credentials_exception

    return account
