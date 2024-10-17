from typing import List
from fastapi import APIRouter, HTTPException
from openg2p_fastapi_common.controller import BaseController
from openg2p_portal_api.models.document_store import DocumentStore
from ..services.documet_store_service import DocumentStoreService

from ..config import Settings
_config = Settings.get_config()

class DocumentStoreController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._store_service = DocumentStoreService.get_component()

        self.router = APIRouter()
        self.router.tags += ["DocumentStore"]

        self.router.add_api_route(
            "/createStore",
            self.create_store,
            responses={200: {"model": DocumentStore}},
            methods=["POST"],
        )

        self.router.add_api_route(
            "/getAllStores",
            self.get_all_stores,
            responses={200: {"model": List[DocumentStore]}},
            methods=["GET"],
        )

    @property
    def store_service(self):
        if not self._store_service:
            self._store_service = DocumentStoreService.get_component()
        return self._store_service


    async def create_store(self,  store: DocumentStore):
        try:
            store = await self.store_service.create_store(store.name, store.server_env_defaults)
            
            return { "store":store}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


    async def get_all_stores(self):
        try:
            stores = await self.store_service.get_all_stores()
            return stores
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
