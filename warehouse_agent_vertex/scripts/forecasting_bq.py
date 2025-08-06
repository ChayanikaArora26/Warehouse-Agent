import pandas as pd
from prophet import Prophet
from google.cloud import bigquery
from scripts.config import config

client = bigquery.Client(project=config.GCP_PROJECT_ID)
sql = f"""SELECT date, sku, picks
           FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.daily_demand`"""
demand_df = client.query(sql).to_dataframe()

def forecast_sku(sku: str, periods: int = 7):
    hist = demand_df[demand_df['sku'] == sku].copy()
    if hist.empty:
        return None
    ts = hist.groupby('date')['picks'].sum().reset_index()
    ts.columns = ['ds', 'y']
    m = Prophet(interval_width=0.95)
    m.fit(ts)
    future = m.make_future_dataframe(periods=periods)
    fc = m.predict(future)[['ds','yhat']].tail(periods)
    fc['sku'] = sku
    return fc.rename(columns={'ds':'date','yhat':'predicted_demand'})

def main():
    frames = []
    for s in demand_df['sku'].unique():
        fc = forecast_sku(s)
        if fc is not None:
            frames.append(fc)
    if not frames:
        print("No forecasts generated."); return
    forecast_all = pd.concat(frames, ignore_index=True)
    table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.demand_forecast"
    job = client.load_table_from_dataframe(
        forecast_all, table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    )
    job.result()
    print("Forecast table updated.")

if __name__ == "__main__":
    main()
