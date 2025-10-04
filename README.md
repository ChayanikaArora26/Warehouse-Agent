#  Warehouse-Agent

**An AI-Powered Warehouse Operations and Pricing Optimization Agent**

---

## 📘 Overview

The **Warehouse-Agent** is an intelligent AI system that automates key warehouse functions like **inventory forecasting**, **days-of-cover computation**, and **dynamic pricing optimization**.  
It connects to **Google BigQuery** for data, uses **Vertex AI** for predictive reasoning, and executes optimization logic in **Python**.

Developed collaboratively by **Chayanika Arora** and **Ajay Rahavendar**, the project demonstrates how an **Agentic AI system** can streamline supply chain management through data-driven decision-making.

---

## 🧠 What the Agent Does

The Warehouse-Agent acts like a digital warehouse manager that:

- 🧾 Analyzes product-level stock and sales data from BigQuery.  
- 📉 Calculates **Days of Cover** (how long current stock will last).  
- 💰 Suggests price adjustments or promotions automatically.  
- 📤 Updates recommendations directly in the BigQuery table.  
- ⚙️ Integrates seamlessly with **Vertex AI pipelines** for automation.

---

## 🧱 Project Structure

```text
Warehouse-Agent/
│
├── warehouse_agent_vertex/           # Core implementation folder
│   ├── pricing_optimizer.py          # Main agent logic - connects to BigQuery, computes days-cover, updates price table
│   ├── utils.py                      # Helper utilities for queries, calculations, and logging
│   ├── config.yaml                   # Configuration file (project, dataset, thresholds)
│
├── Warehouse-Agent.code-workspace    # Optional VS Code workspace config
└── README.md                         # Documentation
```

| File | Description |
|------|--------------|
| **pricing_optimizer.py** | Main agent script. Fetches data from BigQuery, computes stock coverage, and updates price recommendations. |
| **utils.py** | Contains helper functions (query execution, math calculations, and error handling). |
| **config.yaml** | Configuration file storing dataset names, thresholds, and default parameters. |
| **Warehouse-Agent.code-workspace** | VSCode workspace configuration for local development. |
| **README.md** | Documentation file explaining setup, usage, and architecture. |

---

## 🚀 How to Run

### Step 1️⃣ — Environment Setup

1. **Clone the repository**

```bash
git clone https://github.com/ChayanikaArora26/Warehouse-Agent.git
cd Warehouse-Agent
```

2. **(Optional) Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate     # On macOS/Linux
venv\Scripts\activate        # On Windows
```

3. **Install dependencies**

If you have a `requirements.txt` file (recommended):

```bash
pip install -r requirements.txt
```

Or, install manually:

```bash
pip install google-cloud-bigquery argparse pyyaml
```

4. **Authenticate Google Cloud credentials**

```bash
gcloud auth application-default login
```

---

### Step 2️⃣ — Run the Agent

Execute the agent from terminal:

```bash
python warehouse_agent_vertex/pricing_optimizer.py --project <PROJECT_ID> --dataset whadb --days-cover 30
```

**Example:**

```bash
python warehouse_agent_vertex/pricing_optimizer.py --project usyd-warehouse --dataset whadb --days-cover 45
```

---

### Step 3️⃣ — Arguments Reference

| Argument | Description | Default |
|-----------|--------------|----------|
| `--project` | Google Cloud Project ID | *(required)* |
| `--dataset` | BigQuery dataset name | `whadb` |
| `--days-cover` | Number of days to maintain stock coverage | `30` |

---

### ✅ Verification

```json
{
  "product_id": "A123",
  "days_cover": 42.7,
  "recommended_price": 19.99,
  "status": "Price adjusted successfully"
}
```

---

## 💬 What You Can Ask the Agent

When connected to a conversational layer (e.g., **Vertex AI Agent**, **LangChain**, or a custom API interface), you can ask questions like:

- 💬 “How many days of cover does Product A123 have?”  
- 💬 “Which items are overstocked?”  
- 💬 “List products that need promotion this week.”  
- 💬 “Generate dynamic price recommendations.”  
- 💬 “Update all price recommendations in BigQuery.”  
- 💬 “Which SKUs are likely to run out within 10 days?”  
- 💬 “What’s the sales velocity for each product category?”  

---

## 🧩 Example Workflow

| Step | Task | Output |
|------|------|--------|
| 1 | Fetch data from BigQuery | Product-wise stock, demand, and historical prices |
| 2 | Compute Days of Cover | Calculates stock longevity |
| 3 | Optimize Prices | Generates new recommended price |
| 4 | Write Results | Updates `price_recommendations` table |
| 5 | Log Output | Returns confirmation JSON |

---

## 🧭 System Architecture

```text
             ┌──────────────────────────────┐
             │  BigQuery Dataset (whadb)    │
             │  - dim_product               │
             │  - inventory_snapshots       │
             │  - price_recommendations     │
             └──────────────┬───────────────┘
                            │
                            ▼
             ┌──────────────────────────────┐
             │  Warehouse Agent (Python)    │
             │  - Fetches data              │
             │  - Computes days_cover       │
             │  - Optimizes pricing         │
             │  - Updates recommendations   │
             └──────────────┬───────────────┘
                            │
                            ▼
             ┌──────────────────────────────┐
             │  Vertex AI (Prediction API)  │
             │  - Forecasts demand          │
             │  - Detects anomalies         │
             └──────────────────────────────┘
```

---

## ⚙️ Technologies Used

| Category | Technology |
|-----------|-------------|
| **Language** | Python 3.10+ |
| **Cloud Platform** | Google Cloud Platform (GCP) |
| **Data Layer** | BigQuery |
| **AI Layer** | Vertex AI |
| **Libraries** | `google-cloud-bigquery`, `argparse`, `pyyaml`, `math`, `os` |
| **IDE** | Visual Studio Code |
| **Version Control** | Git & GitHub |

---

## 🧠 Future Enhancements

- 🤖 Add **LLM-based conversational interface** for natural queries  
- 🔄 Integrate **Vertex AI Pipelines** for full automation  
- 🧮 Add **Reinforcement Learning** for adaptive pricing  
- 📊 Deploy **Streamlit or Looker Studio dashboards** for visualization  
- 🦆 Integrate **DuckDB + PandasAI** for local ETL and simulations  

---

## 👥 Contributors

| Name | Role | Contribution |
|------|------|--------------|
| **Chayanika Arora**
| **Ajay Rahavendar** 

---

## 📄 License

MIT License © 2025  
**Chayanika Arora** & **Ajay Rahavendar**

---

## 🧾 Acknowledgment

Developed as part of an academic initiative on **Agentic AI for Warehouse Optimization**.  



