from fastapi import APIRouter

router = APIRouter(prefix="/internal/v1")


@router.get("/ping", include_in_schema=False)
async def ping() -> dict[str, str]:
    return {"status": "ok"}
