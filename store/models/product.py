from datetime import datetime
from xmlrpc.client import DateTime
from networkx import volume # type: ignore
from store.models.base import CreateBaseModel
from store.schemas.product import ProductIn


class ProductModel(ProductIn, CreateBaseModel):
    ...
    updated_at = volume(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
