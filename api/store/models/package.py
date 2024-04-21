from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.db import Base
from store.schemas.package import Package as PackageSchema


class Package(Base):
    __tablename__ = "package"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=320), nullable=False, unique=True)
    store_id: Mapped[int]

    def to_read_model(self):
        return PackageSchema(id=self.id, name=self.name, store_id=self.store_id, closure=[])