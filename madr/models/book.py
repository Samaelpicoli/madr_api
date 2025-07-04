from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from madr.database.get_session import table_registry

if TYPE_CHECKING:  # pragma: no cover
    from madr.models.author import Author


@table_registry.mapped_as_dataclass
class Book:
    """
    Modelo de livro para o banco de dados.
    Este modelo representa a tabela de livros no banco de dados
    e contém os campos necessários para armazenar informações
    sobre os livros cadastrados.

    Attributes:
        id (int): ID único do livro (chave primária).
        title (str): Título do livro, deve ser único.
        year (int): Ano de publicação do livro.
        author_id (int): ID do autor do livro (chave estrangeira).
        author (Author): Autor associado ao livro.
        created_at (datetime): Timestamp de criação do livro.
        updated_at (datetime): Timestamp da última atualização do livro.
    """

    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    year: Mapped[int]
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['Author'] = relationship(
        init=False, back_populates='books', lazy='selectin'
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
