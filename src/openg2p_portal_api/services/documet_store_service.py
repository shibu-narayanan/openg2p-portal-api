import json
from typing import Any, Dict
from openg2p_fastapi_common.service import BaseService

from openg2p_portal_api.models.document_store import DocumentStore
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from ..models.orm.document_store_orm import DocumentStoreORM
from openg2p_fastapi_common.context import dbengine
from sqlalchemy.ext.asyncio import  async_sessionmaker
from openg2p_fastapi_common.service import BaseService


class DocumentStoreService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.async_session_maker = async_sessionmaker(dbengine.get())


    async def create_store(self, name: str, server_env_defaults: Dict[str, Any]):
        async with self.async_session_maker() as session:
            new_store = DocumentStoreORM(
                name=name,
                server_env_defaults=server_env_defaults)
            session.add(new_store)

            try:
                await session.commit() 
                await session.refresh(new_store) 
                return DocumentStore.from_orm(new_store)  
            except SQLAlchemyError as e:
                await session.rollback()  
                raise Exception("Error creating backend: " + str(e))


    
    async def get_all_stores(self):
        async with self.async_session_maker() as session:
            try:
                query = select(DocumentStoreORM)
                result = await session.execute(query)
                stores = result.scalars().all()
                for store in stores:
                    store.server_env_defaults = json.loads(store.server_env_defaults)
                return [DocumentStore.from_orm(store) for store in stores]
            except Exception as e:
                raise Exception("Error retrieving stores: " + str(e))
    

