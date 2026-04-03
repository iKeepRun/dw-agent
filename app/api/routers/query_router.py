import asyncio
from socketserver import StreamRequestHandler

from aiohttp.web_response import StreamResponse
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.api.schemas.query_schema import QuerySchema

query_router=APIRouter ()

async def fake_stream():
    for i in range(10):
        await asyncio.sleep(1)
        yield f"data: step:{i}\n\n"



@query_router.post("/api/query")
async def query_handler(query:QuerySchema):
   return StreamingResponse (
       fake_stream(),
       media_type="text/event-stream"
   )
