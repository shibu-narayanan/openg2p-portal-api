from typing import List
from openg2p_fastapi_common.service import BaseService

from openg2p_portal_api.models.documet_tag import DocumentTag
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from ..models.orm.document_tag_orm import DocumentTagORM
from openg2p_fastapi_common.context import dbengine
from sqlalchemy.ext.asyncio import  async_sessionmaker

class DocumentTagService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.async_session_maker = async_sessionmaker(dbengine.get())


  
    async def create_tag(self, tag_name: str):
        async with self.async_session_maker() as session:
                new_tag = DocumentTagORM(name=tag_name)
                session.add(new_tag)

                try:
                    await session.commit() 
                    await session.refresh(new_tag) 
                    return DocumentTag.from_orm(new_tag)  
                except SQLAlchemyError as e:
                    await session.rollback()  
                    raise Exception("Error creating tag: " + str(e))

                
                
    async def get_all_tags(self):
        async with self.async_session_maker() as session:
                try:
                    result = await session.execute(select(DocumentTagORM))
                    tags = result.scalars().all()
                    return [DocumentTag.from_orm(tag) for tag in tags] 
                except Exception as e:
                    raise Exception("Error retrieving tags: " + str(e))


    # async def get_tags_by_name(self, tag_name: str):
    #     async with self.async_session_maker() as session:
    #         result = await session.execute(
    #             select(DocumentTagORM).where(DocumentTagORM.name == tag_name)  
    #         )
    #         return result.scalars().all()