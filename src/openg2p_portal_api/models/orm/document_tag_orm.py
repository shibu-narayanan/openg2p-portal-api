from typing import List
from openg2p_fastapi_common.models import BaseORMModel
from openg2p_portal_api.models.orm.document_file_orm import DocumentFileORM
from sqlalchemy import  String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

class DocumentTagORM(BaseORMModel):
    __tablename__ = "g2p_document_tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    create_uid:Mapped[int] = mapped_column(nullable=False)

    documents: Mapped[List["DocumentFileORM"]] = relationship("DocumentFileORM", back_populates="tag_name")

    __table_args__ = (UniqueConstraint('name', name='name_unique'),)