from pydantic import BaseModel, Field


class FilterPage(BaseModel):
    """
    Modelo para representar filtros de paginação.

    Attributes:
        offset (int): O deslocamento para a paginação, deve ser
        maior ou igual a 0
        limit (int): O número máximo de itens por página, deve ser
        maior ou igual a 0
    """

    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=10)
