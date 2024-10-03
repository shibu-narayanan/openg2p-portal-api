from typing import List
from fastapi import APIRouter, HTTPException
from openg2p_fastapi_common.controller import BaseController
from openg2p_portal_api.models.documet_tag import DocumentTag
from ..config import Settings
from ..services.documet_tag_service import DocumentTagService

_config = Settings.get_config()

class DocumentTagController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._tag_service = DocumentTagService.get_component()
        self.router = APIRouter()
        self.router.tags += ["DocumentStore"]

        self.router.add_api_route(
            "/createTag",
            self.create_tag,
            responses={200: {"model": DocumentTag}},
            methods=["POST"],
        )

        self.router.add_api_route(
            "/getAllTags",
            self.get_tags,
            responses={200: {"model": List[DocumentTag]}},
            methods=["GET"],
        )

    @property
    def tag_service(self):
        if not self._tag_service:
            self._tag_service = DocumentTagService.get_component()
        return self._tag_service

    async def create_tag(self, tag_name: str):
        try:
            tag = await self.tag_service.create_tag(tag_name)
            return {"id": tag.id, "name": tag.name}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


    async def get_tags(self):
        try:
            tags = await self.tag_service.get_all_tags()
            return tags
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
