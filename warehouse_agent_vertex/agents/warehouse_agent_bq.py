"""
Warehouse Agent using Vertex AI + BigQuery (LangChain 0.2+)
------------------------------------------------------------
✅ Compatible with Python 3.11
✅ Works with pydantic>=2.9.2 and google-cloud-aiplatform>=1.61.0
✅ Updated imports for LangChain 0.2.16+ structure
✅ Provides forecast, restock, and cross-sell reasoning
"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ---------------------------
# LangChain + Google imports
# ---------------------------
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase   # ✅ Updated import path

from langchain_google_vertexai import ChatVertexAI

# ---------------------------
# Local project imports
# ---------------------------
from warehouse_agent_vertex.scripts.vertex_init import init_vertex
from warehouse_agent_vertex.scripts.config import config
from warehouse_agent_vertex.scripts.cross_sell_bq import get_cross_sells

from google.cloud import bigquery

# ---------------------------
# Initialize Vertex AI
# ---------------------------
init_vertex()

# ---------------------------
# Database connection (BigQuery)
# ---------------------------
db = SQLDatabase.from_uri(config.SQLALCHEMY_BQ_URI)

# ---------------------------
# LLM setup (Gemini / Vertex AI)
# ---------------------------
llm = ChatVertexAI(
    model=config.VERTEX_MODEL_NAME,
    temperature=0,
    max_output_tokens=2048,
)

# ---------------------------
# SQL tools via LangChain toolkit
# ---------------------------
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = sql_toolkit.get_tools()

# ---------------------------
# Forecast lookup tool
def forecast_overall_next_7_days(_: str = "") -> str:
    """
    Returns demand forecast summary for all SKUs for the next 7 days.
    Automatically detects which forecast column exists in BigQuery.
    """
    client = bigquery.Client(project=config.GCP_PROJECT_ID)
    table_ref = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.demand_forecast"
    
    # 1️⃣ Detect which forecast column actually exists
    table = client.get_table(table_ref)
    colnames = [c.name.lower() for c in table.schema]
    possible_cols = ["predicted_demand", "forecast", "yhat", "demand", "prediction"]
    forecast_col = next((c for c in possible_cols if c in colnames), None)

    if not forecast_col:
        return f"⚠️ No forecast column found in {table_ref}. Columns available: {colnames}"

    # 2️⃣ Build safe query dynamically
    query = f"""
      SELECT 
        sku,
        SUM(`{forecast_col}`) AS total_forecast
      FROM `{table_ref}`
      WHERE date BETWEEN CURRENT_DATE() AND DATE_ADD(CURRENT_DATE(), INTERVAL 7 DAY)
      GROUP BY sku
      ORDER BY total_forecast DESC
      LIMIT 10
    """
    job = client.query(query)
    rows = list(job.result())

    if not rows:
        return "No forecast data found for the next 7 days."

    # 3️⃣ Format the results
    output = "\n".join(
        f"SKU {r.sku}: {int(r.total_forecast)} units expected"
        for r in rows
        if r.total_forecast is not None
    )
    return f"📈 7-Day Demand Forecast Summary (using '{forecast_col}' column):\n{output}"


# ---------------------------
def forecast_lookup(sku: str) -> str:
    """
    Fetches 7-day forecast for a given SKU.
    Auto-detects available forecast column in BigQuery table.
    """
    client = bigquery.Client(project=config.GCP_PROJECT_ID)

    # Step 1: detect which forecast-like columns exist
    table_ref = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.demand_forecast"
    table = client.get_table(table_ref)
    colnames = [f.name.lower() for f in table.schema]

    # Step 2: pick the best forecast column dynamically
    possible_cols = ["predicted_demand", "forecast", "yhat", "demand", "prediction"]
    forecast_col = next((c for c in possible_cols if c in colnames), None)

    if not forecast_col:
        return f"⚠️ No recognized forecast column found in {table_ref}. Columns available: {colnames}"

    # Step 3: run safe query
    query = f"""
      SELECT 
        date,
        `{forecast_col}` AS forecast_value
      FROM `{table_ref}`
      WHERE sku = @sku
      ORDER BY date
      LIMIT 7
    """
    job = client.query(
        query,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("sku", "STRING", sku)]
        ),
    )

    rows = list(job.result())
    if not rows:
        return f"No forecast available for {sku} in {forecast_col}."

    output = " | ".join(
        f"{r.date}: {int(r.forecast_value)}"
        for r in rows
        if r.forecast_value is not None
    )
    return f"📊 Forecast for {sku} ({forecast_col}): {output}"

forecast_all_tool = Tool(
    name="ForecastAll",
    func=forecast_overall_next_7_days,
    description="Get total 7-day demand forecast summary for all SKUs (no input required).",
)

forecast_tool = Tool(
    name="ForecastLookup",
    func=forecast_lookup,
    description="Get next 7-day demand forecast for a SKU (input: SKU ID).",
)

# ---------------------------
# Restock tool (human-in-loop)
# ---------------------------
def trigger_restock_with_gate(payload: str) -> str:
    """
    Handles restock like 'restock SKU123 200'.
    Adds to BigQuery pending_actions if > MAX_AUTO_RESTOCK.
    """
    parts = payload.split()
    if len(parts) < 3:
        return "Usage: 'restock <SKU> <amount>'"

    sku, amt = parts[1], int(parts[2])
    client = bigquery.Client(project=config.GCP_PROJECT_ID)

    if amt > config.MAX_AUTO_RESTOCK:
        table = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.pending_actions"
        rows_to_insert = [{"action_type": "RESTOCK", "sku": sku, "amount": amt}]
        errors = client.insert_rows_json(table, rows_to_insert)
        if errors:
            return f"⚠️ Error inserting pending action: {errors}"
        return f"🕐 Restock for {sku} ({amt}) pending approval."
    else:
        return f"✅ Auto-approved restock for {sku}, quantity {amt}."

restock_tool = Tool(
    name="RestockOrder",
    func=trigger_restock_with_gate,
    description="Place restock order '<SKU> <amount>' (auto if ≤ threshold, else approval).",
)

# ---------------------------
# Cross-sell tool
# ---------------------------
def cross_sell_suggest(sku: str) -> str:
    """
    Suggests complementary SKUs based on cross-sell analysis.
    """
    try:
        results = get_cross_sells(sku)
        if not results:
            return f"No cross-sell items found for {sku}."
        return " | ".join(results)
    except Exception as e:
        return f"[ERROR: Cross-sell failed for {sku}] {e}"

cross_sell_tool = Tool(
    name="CrossSellSuggest",
    func=cross_sell_suggest,
    description="Suggest cross-sell items for a SKU (input: SKU ID).",
)

# ---------------------------
# Combine tools & initialize agent
# ---------------------------
tools = sql_tools + [forecast_tool, forecast_all_tool, restock_tool, cross_sell_tool]


agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# ---------------------------
# Standalone test
# ---------------------------
if __name__ == "__main__":
    q = "List SKUs below safety stock and suggest restocks for next week"
    print(agent.run(q))
