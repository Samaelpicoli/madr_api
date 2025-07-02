from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from madr.schemas.page_schema import FilterPage
from madr.utils.sanitize_data import sanitize_text_in


class BookSchema(BaseModel):
    """
    Modelo para representar a criação de um livro.
    Este modelo é utilizado para validar os dados de entrada ao criar um livro.

    Attributes:
        title (str): O título do livro
        year (int): O ano de publicação do livro
        author_id (int): O ID do autor do livro
    """

    title: str
    year: int
    author_id: int

    @field_validator('title')
    def sanitize_book_title(cls, text: str):
        """
        Sanitiza o título do livro antes de armazená-lo.
        Esta função remove caracteres indesejados e formata o texto
        para garantir que o título esteja em um formato adequado.

        Args:
            text (str): O título do livro a ser sanitizado.

        Returns:
            str: O título sanitizado.
        """
        return sanitize_text_in(text)


class BookPublic(BookSchema):
    """
    Este modelo é utilizado para retornar informações sobre o livro.
    Ele herda de BookSchema e adiciona o campo id,
    que é o identificador único do livro.

    Attributes:
        id (int): O ID do livro
        model_config (ConfigDict): Configuração do modelo para permitir
        a criação a partir de atributos.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


class BookList(BaseModel):
    """
    Modelo para representar uma lista de livros a partir do Schema BookPublic.

    Attributes:
        books (List[BookPublic]): Lista de livros
    """

    books: List[BookPublic]


class BookUpdate(BaseModel):
    """
    Modelo para atualizar informações de um livro.
    Este modelo é utilizado para validar os dados de entrada ao
    atualizar um livro.

    Attributes:
        title (str | None): O título do livro (opcional)
        year (int | None): O ano de publicação do livro (opcional)
        author_id (int | None): O ID do autor do livro (opcional)
    """

    title: str | None = None
    year: int | None = None
    author_id: int | None = None

    @field_validator('title')
    def sanitize_book_title(cls, text: str):
        """
        Sanitiza o título do livro antes de armazená-lo.
        Esta função remove caracteres indesejados e formata o texto
        para garantir que o título esteja em um formato adequado.

        Args:
            text (str): O título do livro a ser sanitizado.

        Returns:
            str: O título sanitizado.
        """
        return sanitize_text_in(text)


class FilterBook(FilterPage):
    """
    Modelo para filtrar livros com base em critérios específicos.
    Este modelo é utilizado para validar os dados de entrada ao filtrar livros.

    Attributes:
        author_id (int | None): O ID do autor do livro (opcional)
        title (str | None): O título do livro (opcional)
        year (int | None): O ano de publicação do livro (opcional)
        limit (int): O número máximo de livros a serem retornados
    """

    title: str | None = Field(default=None, min_length=1)
    year: int | None = None
    limit: int = Field(ge=1, default=20)
