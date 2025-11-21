from .BaseController import BaseController
from models.db_schemas import User, Chunk
from sentence_transformers import SentenceTransformer 
from typing import List

class NLPController(BaseController):
    def __init__(self, vectordb_client):
        super().__init__()
        
        self.vectordb_client = vectordb_client
        self.embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.embedding_size = 384
        
                
    def create_collection_name(self, user_id: str):
        return f"collection_{user_id}".strip()
    
    def reset_vector_db_collection(self, user: User):
        collection_name = self.create_collection_name(
            user_id=user.user_id,
        )
        return self.vectordb_client.delete_collection(
            collection_name=collection_name
        )

    def index_info_vector_db(self, user: User, chunks: List[Chunk],
                              chunks_ids: List[int], do_reset: bool = False):
        
        # step1: get collection name
        collection_name = self.create_collection_name(user_id=user.user_id)
        
        # step2: manage items
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = [
            self.embed_model.encode(text)
            for text in texts
        ]
        
        # step3: create collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_size,
            do_reset=do_reset,
        )
        
        # step4: insert intp vector db
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True