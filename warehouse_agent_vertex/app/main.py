from fastapi import FastAPI
from warehouse_agent_vertex.app.routes import router

app = FastAPI(title="Warehouse AI Agent API", version="1.0.1")

app.include_router(router)
