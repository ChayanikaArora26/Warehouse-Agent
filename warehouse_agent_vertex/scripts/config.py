# warehouse_agent_vertex/scripts/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration for Warehouse Agent"""

    # GCP / BigQuery
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "alpine-alpha-467613-k9")
    BQ_DATASET = os.getenv("BQ_DATASET", "whadb")

    # Vertex AI
    VERTEX_PROJECT_ID = os.getenv("VERTEX_PROJECT_ID", "alpine-alpha-467613-k9")
    VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
    VERTEX_MODEL_NAME = os.getenv(
        "VERTEX_MODEL_NAME", "publishers/google/models/gemini-2.5-flash-lite"
    )

    # SQLAlchemy + BigQuery dialect
    SQLALCHEMY_BQ_URI = f"bigquery://{GCP_PROJECT_ID}/{BQ_DATASET}"

    # Optional OpenAI key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Agent parameters
    MAX_AUTO_RESTOCK = int(os.getenv("MAX_AUTO_RESTOCK", "100"))

# ✅ export this for easy import
config = Config()
