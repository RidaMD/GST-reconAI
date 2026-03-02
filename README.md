# GST ReconAI

A comprehensive Knowledge Graph-based GST Reconciliation and Fraud Detection platform. This system leverages Neo4j to map relationships between Taxpayers, GSTINs, Invoices, and Returns to identify mismatches, behavioral risks, and financial exposure.

## Features

- **Knowledge Graph Visualization**: Interactive 2D graph of GST entities and their relationships.
- **Financial Risk Scorer**: Tabular view of invoices with automated risk scoring and compliance flags.
- **Predictive Vendor Risk**: Machine learning-based risk assessment for suppliers based on historical behavior.
- **Compliance Flags**: Automated identification of errors such as:
  - Match
  - Excess ITC Claim
  - GST Under-Claim
  - Return Not Filed
  - GST Mismatch
- **AI-Powered Audit Support**: Integration for generating NLP-based audit reports.
- **Flexible Data Ingestion**: Supports both multi-file and consolidated CSV mock data.

## Project Structure

- `backend/`: FastAPI-powered backend with Neo4j integration and reconciliation logic.
- `frontend/`: React-based dashboard with interactive graph and analytics components.
- `mock data/`: Standard sample data for testing the reconciliation engine.

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js & npm
- Neo4j Database

### Setup

1. **Environment Variables**:
   Create a `.env` file in the `backend/` directory:
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   OPENAI_API_KEY=your_key
   ```

2. **Ingest Data**:
   ```bash
   cd backend
   python csv_ingestion.py
   ```

3. **Run Backend**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

4. **Run Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## License

MIT
