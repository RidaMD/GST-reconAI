# GST ReconAI 🛡️

**GST ReconAI** is a Knowledge Graph-based GST Reconciliation and Fraud Detection platform designed for high-precision audit preparation and vendor risk assessment.

## 🏗️ Architecture OVERVIEW

The system is built on a modern, decoupled architecture designed for graph-relational data processing:

-   **Frontend**: React (Vite) + `react-force-graph-2d` for interactive visualization.
-   **Backend**: FastAPI (Python) for high-performance API handling.
-   **Database**: Neo4j (Graph Database) for mapping complex multi-hop supply chain relationships.
-   **Risk Engine**: A custom Python-based structural and behavioral audit engine.

---

## ✨ Key Features

-   **Knowledge Graph Visualization**: Interactive 2D graph mapping relationships between Taxpayers, GSTINs, Invoices, and Returns.
-   **Financial Risk Scorer**: Ranked dashboard of invoices with automated risk scoring and color-coded compliance flags.
-   **Behavioral Vendor Risk**: Risk assessment for suppliers based on historical transaction patterns and filing behavior (GSTR-1/3B consistency).
-   **AI Audit Support**: Integration with **OpenAI (GPT-4o-mini)** for generating natural-language audit narratives based on graph-extracted risk nodes.
-   **Compliance Flags**:
    -   `Match`: Perfect alignment across GSTR-1, 2B, and PR.
    -   `Excess ITC Claim`: ITC claimed exceeds the supplier's filed GST.
    -   `Return Not Filed`: Invoice exists but no corresponding GSTR-1 found.
    -   `GST Mismatch`: Discrepancy between supplier-reported and buyer-claimed GST.

---

## 📊 Sample Insights

### Risk Scoring Formula
The system calculates a `total_risk` score based on Structural (SP) and Behavioral (BP) points, scaled by a Financial Exposure multiplier:

```python
# Multiplier based on relative invoice amount
total_risk = (structural_points + behavioral_points) * multiplier

if perc_of_max < 0.20: multiplier = 1.0
elif perc_of_max <= 0.50: multiplier = 1.2
elif perc_of_max <= 0.80: multiplier = 1.5
else: multiplier = 1.8
```

### Sample API Output (Scorer)
```json
{
  "invoice_id": "INV005",
  "supplier_name": "Supplier_GST1005",
  "gst_invoice": 16200.0,
  "gst_paid": 18000.0,
  "risk_score": 300,
  "risk_level": "CRITICAL",
  "root_cause": "Return Not Filed | Excess ITC Claim | GST Mismatch | Missing 2B"
}
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+ 
- Node.js + npm
- Neo4j Instance (Local or Aura)

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python csv_ingestion.py # Populates graph
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🛠️ Performance & Stability
In the event of a backend or database connectivity issue, the frontend is designed to gracefully degrade, showing persistent mock data placeholders to ensure presentation continuity.

## 📄 License
MIT
