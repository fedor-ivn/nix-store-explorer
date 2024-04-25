from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.db import Base
from src.store.schemas.store import Store as StoreSchema


class Store(Base):
    __tablename__ = "store"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(length=320), nullable=False, unique=True)
    owner_id: Mapped[int] = mapped_column(Integer)

    def to_read_model(self):
        return StoreSchema(id=self.id, name=self.name, owner_id=self.owner_id)
