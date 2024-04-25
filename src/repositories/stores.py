from src.store.models.package import Package
from src.store.models.store import Store
from src.utils.repository import SQLAlchemyRepository


class StoreRepository(SQLAlchemyRepository):
    model = Store


class PackageRepository(SQLAlchemyRepository):
    model = Package
