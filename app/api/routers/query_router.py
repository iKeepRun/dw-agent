import asyncio
from socketserver import StreamRequestHandler
from typing import Annotated

from fastapi import APIRouter, Depends, Body
from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService

query_router=APIRouter ()

@query_router.post("/api/query")
async def query_handler(
        query_data:Annotated[QuerySchema,Body()],
        query_service:Annotated[QueryService ,Depends(get_query_service)]):

   return StreamingResponse (
       query_service.query(query_data.query),
       media_type="text/event-stream"
   )
