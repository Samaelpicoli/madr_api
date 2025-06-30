from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from madr.database.get_session import table_registry

if TYPE_CHECKING:
    from madr.models.author import Author


@table_registry.mapped_as_dataclass
class Book:
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    year: Mapped[int]
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['Author'] = relationship(init=False, back_populates='books')
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
