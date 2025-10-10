from google.cloud import bigquery
from warehouse_agent_vertex.scripts.config import config


client = bigquery.Client(project=config.GCP_PROJECT_ID)

def get_cross_sells(sku: str, top_n: int = 3) -> str:
    query = f"""
    SELECT
      IF(sku_a = @sku, sku_b, sku_a) AS suggested_sku,
      pair_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.cross_sell_pairs`
    WHERE sku_a = @sku OR sku_b = @sku
    ORDER BY pair_count DESC
    LIMIT {top_n};
    """
    job = client.query(query, job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("sku", "STRING", sku)]
    ))
    rows = job.result()
    suggestions = [r.suggested_sku for r in rows]
    return (f"Cross-sell for {sku}: {', '.join(suggestions)}"
            if suggestions else f"No cross-sell data for {sku}.")
