from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from openg2p_fastapi_common.models import BaseORMModel

class DocumentFileORM(BaseORMModel):
    __tablename__ = "storage_file"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    backend_id: Mapped[int] = mapped_column(ForeignKey("storage_backend.id"), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String, nullable=True, index=True)
    relative_path: Mapped[str] = mapped_column(String, nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    human_file_size: Mapped[str] = mapped_column(String, nullable=True)
    checksum: Mapped[str] = mapped_column(String(40), nullable=True, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=True) 
    extension: Mapped[str] = mapped_column(String, nullable=True)
    mimetype: Mapped[str] = mapped_column(String, nullable=True) 
    to_delete: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    file_type: Mapped[str] = mapped_column(String, nullable=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("res_partner.id"), nullable=True)  
    create_uid: Mapped[int] = mapped_column(ForeignKey("g2p_document_tag.create_uid"), nullable=True)  
  

    backend = relationship("DocumentStoreORM", back_populates="documents")
    partner = relationship("PartnerORM", back_populates='documents')
    tag_name = relationship("DocumentTagORM", back_populates='documents')

    __table_args__ = (UniqueConstraint('relative_path', 'backend_id', name='path_uniq'),)

    
   