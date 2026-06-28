from fastapi import APIRouter

from app.api.rest.routers.internal.v1.ping.schemas import V1PingOutputSchema

router = APIRouter(prefix="/ping", tags=["Internal"])


@router.get("", response_model=V1PingOutputSchema, include_in_schema=False)
async def ping() -> V1PingOutputSchema:
    return V1PingOutputSchema(status="ok")
