from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from madr.database.get_session import table_registry

if TYPE_CHECKING:
    from madr.models.book import Book


@table_registry.mapped_as_dataclass
class Author:
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    books: Mapped[List['Book']] = relationship(
        init=False, back_populates='author', cascade='all, delete-orphan'
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
