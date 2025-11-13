from fastapi import FastAPI
from routes import base, ingest

app = FastAPI()

app.include_router(base.base_router)
app.include_router(ingest.ingest_router)