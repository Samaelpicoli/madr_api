from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from madr.utils.sanitize_data import sanitize_text_in


class AccountSchema(BaseModel):
    """
    Modelo para representar a criação de uma conta de usuário.

    Attributes:
        username (str): O nome de usuário
        email (str): O endereço de e-mail do usuário
        password (str): A senha do usuário
    """

    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    def sanitize_username(cls, text: str):
        return sanitize_text_in(text)


class AccountPublic(BaseModel):
    """
    Modelo para representar uma resposta quando é criado o usuário,
    sem expor a senha.

    Attributes:
        id (int): O ID do usuário
        username (str): O nome de usuário
        email (str): O endereço de e-mail do usuário
        model_config (ConfigDict): Configuração do modelo
        Esta configuração permite que o modelo seja criado a partir de
        atributos, o que é útil para criar instâncias do modelo a partir
        de dicionários ou outros objetos que possuem os mesmos atributos.
    """

    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class AccountList(BaseModel):
    """
    Modelo para representar uma lista de usuários a partir do Schema
    AccountPublic.

    Attributes:
        accounts (List[AccountPublic]): Lista de contas de usuário
    """

    accounts: List[AccountPublic]
