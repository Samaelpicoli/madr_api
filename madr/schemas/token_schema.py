from pydantic import BaseModel


class Token(BaseModel):
    """
    Modelo para representar um token JWT.
    Utilizado para autenticação e autorização de usuários.

    Attributes:
        access_token (str): O token de acesso JWT
        token_type (str): O tipo do token, geralmente 'bearer'
    """

    access_token: str
    token_type: str
