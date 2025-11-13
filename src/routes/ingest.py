from fastapi import APIRouter, status
from pydantic import BaseModel, HttpUrl
from fastapi.responses import JSONResponse
from controllers.DataController import DataController 

ingest_router = APIRouter()

class IngestRequest(BaseModel):
    url: HttpUrl


@ingest_router.post("/ingest/{user_id}")
async def ingest_urls(user_id: str, ingest_request: IngestRequest):
    data_controller = DataController()

    youtube_url = ingest_request.url

    audio_path = data_controller.generate_audio_path(user_id)

    success, signal = data_controller.download_youtube_audio(youtube_url, audio_path)

    if success:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "signal": signal,
                "audio_path": audio_path,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "signal": signal,
        },
    )
