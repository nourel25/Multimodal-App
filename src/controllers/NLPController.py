from .BaseController import BaseController
from models.db_schemas import User, Chunk
from sentence_transformers import SentenceTransformer 
from typing import List
import ollama

class NLPController(BaseController):
    def __init__(self, vectordb_client, template_parser, generation_client):
        super().__init__()
        
        self.vectordb_client = vectordb_client
        self.embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.embedding_size = 384
        self.template_parser = template_parser
        self.generate_model = "llama3.2:1b-instruct-q8_0"
        self.generation_client = generation_client
        
                
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
    
    def search_vector_db_collection(self, user: User, text: str, limit: int = 3):
        
        # step1: get collection name
        collection_name = self.create_collection_name(user_id=user.user_id)
        
        # step2: get text embedding vector
        vector = self.embed_model.encode(text)
        
        if vector is None or vector.shape[0] == 0:
            return False
        
        # step3: do sematic search
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector.tolist(),
            limit=limit,
        )
        
        print(results)
        
        if not results:
            return False
        
        return results
    
    def generate_answer(self, messages: list[dict]):
        # Initialize the client once
        response = self.generation_client.chat(
            model=self.generate_model,
            messages=messages
        )
        
        return response['message']['content']        
    
    def answer_rag_question(self, language:str, user: User, query: str, limit: int = 5):
        
        answer, full_prompt, chat_history = None, None, None
        
        self.template_parser.set_language(language=language)
        
        # step1: Retrieve related documents
        retrieved_documents = self.search_vector_db_collection(
            user=user,
            text=query,
            limit=limit
        )
        
        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step2: Construct LLM prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")
        
        documents_prompts = "\n".join(
            self.template_parser.get(
                group="rag",
                key="document_prompt",
                vars={
                    "doc_num": idx +1,
                    "chunk_text": doc.text,
                }
            )
            for idx, doc in enumerate(retrieved_documents)
        )
        
        footer_prompt = self.template_parser.get(
            group="rag",
            key="footer_prompt", 
            vars={"query": query}
        )
        
        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt ])
        messages = [
            {"role": "sytem", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ]
        
        answer = self.generate_answer(messages=messages)
        
        return answer, full_prompt, messages