from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

# Controllers
from controllers.NLPController import NLPController

# Models
from models.UserModel import UserModel
from models.ChunkModel import ChunkModel

# Request Schemas
from .schemas.nlp import PushRequest

# Enums
from models.enums.ResponseEnum import ResponseSignal


nlp_router = APIRouter()

@nlp_router.post("/index/push/{user_id}")
async def index_user(request: Request, user_id: str, push_request: PushRequest):
    
    user_model = UserModel(
        db_client=request.app.db_client
    )
    chunk_model = ChunkModel(
        db_client=request.app.db_client
    )
    
    user = await user_model.get_user(user_id)
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.USER_NOT_FOUND.value
            }
        )
        
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
    )
    
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0
    
    while has_records:
        page_chunks = await chunk_model.get_user_chunks(
            user_id=user.id, page_no=page_no,
        )
        
        if len(page_chunks):
            page_no += 1
            
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
            
        chunks_ids =  list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = nlp_controller.index_info_vector_db(
            user=user,
            chunks=page_chunks,
            chunks_ids=chunks_ids,
            do_reset=push_request.do_reset
        )
        
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                }
            )
        
        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )
            