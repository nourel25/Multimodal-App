from pydantic import BaseModel, HttpUrl
from typing import Optional

class IngestRequest(BaseModel):
    youtube_url: HttpUrl
