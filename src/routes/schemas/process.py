from pydantic import BaseModel
from typing import Optional
from bson import ObjectId

class ProcessRequest(BaseModel):
    youtube_url: str
    do_reset: Optional[int] = 0
 
