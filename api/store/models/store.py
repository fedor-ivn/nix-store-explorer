from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from db.db import Base


class Store(Base):
    __tablename__ = "store"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(length=320), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer)
