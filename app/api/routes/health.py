from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.core.container import ApplicationContainer
from app.models.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health_check(container: ApplicationContainer = Depends(get_container)) -> HealthResponse:
    stats = container.qdrant_service.get_stats()
    return HealthResponse(
        status="ok",
        app_name=container.settings.app_name,
        collection_name=stats["collection_name"],
        vector_count=stats["vector_count"],
        unique_files=stats["unique_files"],
    )

