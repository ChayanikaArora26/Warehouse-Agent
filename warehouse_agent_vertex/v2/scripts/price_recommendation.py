#!/usr/bin/env python3
from google.cloud import bigquery
from datetime import datetime
import math, argparse

def calculate_demand_score(units_sold, stock_level):
    if stock_level == 0:
        return 1.5
    ratio = units_sold / stock_level
    return min(1.5, max(0.5, 1 + 0.5 * ratio))

def recommend_price(unit_price, demand_score):
    if demand_score > 1.2:
        return round(unit_price * (1 + 0.05 * (demand_score - 1)), 2)
    elif demand_score < 0.8:
        return round(unit_price * (1 - 0.05 * (1 - demand_score)), 2)
    else:
        return round(unit_price * (1 + 0.02 * (demand_score - 1)), 2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="alpine-alpha-467613-k9")
    parser.add_argument("--dataset", default="whadb")
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    ds = f"{args.project}.{args.dataset}"

    query = f"""
        SELECT 
            product_id,
            AVG(unit_price) AS avg_price,
            AVG(units_sold) AS avg_sold,
            AVG(stock_level) AS avg_stock,
            ANY_VALUE(category) AS category
        FROM `{ds}.sales_history`
        WHERE sale_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY product_id
    """
    rows = client.query(query).result()

    recommendations = []
    for row in rows:
        demand_score = calculate_demand_score(row.avg_sold, row.avg_stock)
        rec_price = recommend_price(row.avg_price, demand_score)
        reason = f"Demand score {demand_score:.2f} → Adjusted from {row.avg_price:.2f}"
        confidence = round(0.75 + abs(demand_score - 1) * 0.25, 2)

        recommendations.append({
            "product_id": row.product_id,
            "recommended_price": rec_price,
            "confidence_score": confidence,
            "last_updated": datetime.utcnow().isoformat(),
            "reason": reason
        })

    client.insert_rows_json(f"{ds}.price_recommendation", recommendations)
    print("✅ Pricing recommendations updated successfully.")

if __name__ == "__main__":
    main()

