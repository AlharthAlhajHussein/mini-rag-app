from fastapi import APIRouter, Depends
from helpers.config import get_settings, Settings
from views.base import BaseResponse

base_router = APIRouter(
    prefix='/api/v1',
    tags=['api_v1']
)

@base_router.get(
    "/",
    response_model=BaseResponse,
    summary="Welcome Endpoint",
    description="Returns a welcome message with application name and version. Used for health checks."
)
async def welcome(app_settings: Settings = Depends(get_settings)):
    return BaseResponse(
        app_name=app_settings.APP_NAME,
        app_version=app_settings.APP_VERSION
    )
 