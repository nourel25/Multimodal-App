from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    do_reset: Optional[int] = 0
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
     
