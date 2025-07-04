from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from madr.database.get_session import table_registry

if TYPE_CHECKING:  # pragma: no cover
    from madr.models.book import Book


@table_registry.mapped_as_dataclass
class Author:
    """
    Modelo de autor para o banco de dados.
    Este modelo representa a tabela de autores no banco de dados
    e contém os campos necessários para armazenar informações
    sobre os autores cadastrados.

    Attributes:
        id (int): ID único do autor (chave primária).
        name (str): Nome do autor, deve ser único.
        books (List[Book]): Lista de livros associados ao autor.
        created_at (datetime): Timestamp de criação do autor.
        updated_at (datetime): Timestamp da última atualização do autor.
    """

    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    books: Mapped[List['Book']] = relationship(
        init=False,
        back_populates='author',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
