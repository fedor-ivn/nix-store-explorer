from store.models.store import Store
from utils.repository import SQLAlchemyRepository


class StoreRepository(SQLAlchemyRepository):
    model = Store
