from typing import List
from uuid import UUID
from datetime import datetime
import pymongo # type: ignore
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase # type: ignore
from pymongo.errors import DuplicateKeyError # type: ignore

from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.core.exceptions import NotFoundException

class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        try:
            product_model = ProductModel(**body.dict())
            await self.collection.insert_one(product_model.dict())
            return ProductOut(**product_model.dict())
        except DuplicateKeyError as e:
            raise NotFoundException(message=f"Duplicate entry detected: {str(e)}")
        except Exception as e:
            raise NotFoundException(message=f"Failed to create product: {str(e)}")

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id})
        if not result:
            raise NotFoundException(message=f"Product not found with ID: {id}")
        return ProductOut(**result)

    async def query(self, min_price: float = None, max_price: float = None) -> List[ProductOut]:
        query = {}
        if min_price is not None and max_price is not None:
            query['price'] = {'$gt': min_price, '$lt': max_price}
        elif min_price is not None:
            query['price'] = {'$gt': min_price}
        elif max_price is not None:
            query['price'] = {'$lt': max_price}
        return [ProductOut(**item) async for item in self.collection.find(query)]

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
        body.updated_at = datetime.utcnow()  # Ensure updated_at is set to current UTC time
        result = await self.collection.find_one_and_update(
            filter={"id": id},
            update={"$set": body.dict(exclude_unset=True)},
            return_document=pymongo.ReturnDocument.AFTER
        )
        if not result:
            raise NotFoundException(message=f"Product not found with ID: {id}")
        return ProductUpdateOut(**result)

    async def delete(self, id: UUID) -> bool:
        result = await self.collection.delete_one({"id": id})
        if result.deleted_count == 0:
            raise NotFoundException(message=f"Product not found with ID: {id}")
        return True

# Instantiation of the ProductUsecase if needed elsewhere
product_usecase = ProductUsecase()
