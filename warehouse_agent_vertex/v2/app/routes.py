from fastapi import APIRouter, Request, Query
from warehouse_agent_vertex.agents import warehouse_agent_bq as agent
from warehouse_agent_vertex.scripts.config import config

router = APIRouter()

# ✅ GET endpoint for quick browser/curl testing
@router.get("/ask")
def ask_get(prompt: str = Query(..., description="Question for the warehouse agent")):
    """Ask the agent using a GET request."""
    result = agent.agent.run(prompt)
    return {"response": result}

# ✅ POST endpoint for API clients / JSON calls
@router.post("/ask")
async def ask_post(request: Request):
    """Ask the agent using a POST request with JSON body."""
    data = await request.json()
    prompt = data.get("prompt", "")
    result = agent.agent.run(prompt)
    return {"response": result}
