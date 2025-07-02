from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from madr.schemas.page_schema import FilterPage
from madr.utils.sanitize_data import sanitize_text_in, sanitize_text_out


class AuthorSchema(BaseModel):
    """
    Modelo para representar a criação de um autor.

    Attributes:
        name (str): O nome do autor.
    """

    name: str

    @field_validator('name')
    def sanitize_name(cls, text: str):
        """
        Sanitiza o nome do autor antes de armazená-lo.
        Esta função remove caracteres indesejados e formata o texto
        para garantir que o nome esteja em um formato adequado.

        Args:
            text (str): O nome do autor a ser sanitizado.

        Returns:
            str: O nome sanitizado.
        """
        return sanitize_text_in(text)


class AuthorPublic(AuthorSchema):
    """
    Modelo para representar um autor público, sem expor detalhes sensíveis.

    Attributes:
        id (int): O ID do autor.
        model_config (ConfigDict): Configuração do modelo para permitir
        a criação a partir de atributos.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)

    @field_validator('name')
    def sanitize_name(cls, text: str) -> str:
        """
        Sanitiza o nome do autor para exibição pública.

        Args:
            text (str): O nome do autor a ser sanitizado.

        Returns:
            str: O nome sanitizado para exibição pública.
        """
        return sanitize_text_out(text)


class AuthorList(BaseModel):
    """
    Modelo para representar uma lista de autores.

    Attributes:
        authors (List[AuthorPublic]): Lista de autores públicos.
    """

    authors: List[AuthorPublic]


class AuthorUpdate(BaseModel):
    """
    Modelo para representar a atualização de um autor.

    Attributes:
        name (str | None): O nome do autor a ser atualizado.
    """

    name: str | None = None

    @field_validator('name')
    def sanitize_username(cls, text: str):
        """
        Sanitiza o nome do autor para exibição pública.

        Args:
            text (str): O nome do autor a ser sanitizado.

        Returns:
            str: O nome sanitizado para exibição pública.
        """
        return sanitize_text_out(text)


class FilterAuthor(FilterPage):
    """
    Modelo para filtrar autores com base em critérios específicos.
    Este modelo é utilizado para validar os dados de
    entrada ao filtrar autores.

    Attributes:
        name (str | None): O nome do autor (opcional).
        limit (int): O número máximo de autores a serem retornados.
    """

    name: str | None = Field(default=None, min_length=1)
    limit: int = Field(ge=1, default=20)
