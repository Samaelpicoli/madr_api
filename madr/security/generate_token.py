from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jwt import encode

from madr.settings.settings import Settings

settings = Settings()


def create_access_token(data: dict) -> str:
    """
    Cria um token de acesso JWT com os dados fornecidos.
    Esta função gera um token JWT (JSON Web Token) que pode ser usado para
    autenticação e autorização de usuários. O token inclui uma data
    de expiração definida por ACCESS_TOKEN_EXPIRE_MINUTES, que é o
    tempo em minutos que o token será válido.

    Args:
        data (dict): Os dados a serem incluídos no token. Normalmente, isso
        inclui informações do usuário, como ID e email.

    Returns:
        str: O token de acesso JWT codificado.
    """
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
