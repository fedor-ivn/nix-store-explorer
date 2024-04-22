from store.models.package import Package
from store.models.store import Store
from utils.repository import SQLAlchemyRepository


class StoreRepository(SQLAlchemyRepository):
    model = Store


class PackageRepository(SQLAlchemyRepository):
    model = Package
