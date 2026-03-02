from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from orchestrator import run_reconciliation
import os
import shutil
import csv_ingestion # To trigger re-ingestion if we want

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
app = FastAPI(title="GST Reconciliation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_gst_data(files: List[UploadFile] = File(...)):
    """
    Accepts CSV files from the React UI Upload component,
    saves them to the mock data folder, and optionally triggers Neo4j ingestion.
    """
    upload_dir = "../mock data"
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        file_location = os.path.join(upload_dir, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    # As requested: "create knowledge graph using it"
    # We trigger the Neo4j script via the driver
    try:
        with driver.session() as session:
            session.execute_write(csv_ingestion.clear_db)
            session.execute_write(csv_ingestion.ingest_from_csv)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {"status": "success", "message": f"Successfully uploaded {len(files)} files and refreshed the graph."}

@app.get("/audit-report/{invoice_id}")
def generate_audit(invoice_id: str):
    """
    Finds the exact invoice mismatch and generates a Langchain AI Audit report.
    """
    import agents
    mismatches = run_reconciliation().get("mismatches", [])
    invoice_data = next((m for m in mismatches if m["invoice_id"] == invoice_id), None)
    
    if not invoice_data:
        return {"error": f"Invoice {invoice_id} not found in mismatch list."}
        
    report_md = agents.generate_audit_report(invoice_data)
    return {"invoice_id": invoice_id, "report_markdown": report_md, "raw_data": invoice_data}

class Mismatch(BaseModel):
    invoice_id: str
    supplier_name: str
    supplier_gstin: str
    buyer_gstin: str
    amount_invoice: float
    gst_invoice: float
    gst_paid: float
    risk_score: float
    risk_level: str
    root_cause: str

def find_gst_mismatches(tx):
    query = """
    MATCH (i:Invoice)
    OPTIONAL MATCH (b:Invoice {invoice_id: i.invoice_id})
    RETURN i.invoice_id AS invoice_id, i.gstin AS supplier_gstin, b.gstin AS buyer_gstin,
           i.gst_amount AS gst_invoice, b.gst_amount AS gst_paid
    """
    results = []
    for record in tx.run(query):
        gst_invoice = record["gst_invoice"] or 0
        gst_paid = record["gst_paid"] or 0
        diff = abs(gst_invoice - gst_paid)
        if diff == 0:
            risk = "No Risk"
        elif diff <= 50:
            risk = "Low Risk"
        elif diff <= 200:
            risk = "Medium Risk"
        else:
            risk = "High Risk"
        results.append(Mismatch(
            invoice_id=record["invoice_id"],
            supplier_name="Unknown", # Placeholder for the basic API, actually populated by reconciliation
            supplier_gstin=record["supplier_gstin"],
            buyer_gstin=record["buyer_gstin"] or "Unknown",
            amount_invoice=gst_invoice,
            gst_invoice=gst_invoice,
            gst_paid=gst_paid,
            risk_score=0.0,
            risk_level=risk,
            root_cause="Clean"
        ))
    return results

@app.get("/mismatches", response_model=List[Mismatch])
def mismatches_api():
    return run_reconciliation()["mismatches"]

@app.get("/graph-data")
def get_graph_data():
    """
    Returns the knowledge graph in a nodes/links adjacency format
    suitable for UI libraries like react-force-graph.
    """
    with driver.session() as session:
        # Fetch a structured subgraph to prevent hairballing while retaining relationships
        query = """
        MATCH (i:Invoice)
        WITH i LIMIT 60
        MATCH p=(i)-[r]-(m)
        WITH startNode(r) AS src, endNode(r) AS tgt, type(r) AS rel_type
        
        // Try to find taxpayer names for GSTIN nodes
        OPTIONAL MATCH (src_t:Taxpayer)-[:HAS_GSTIN]->(src)
        OPTIONAL MATCH (tgt_t:Taxpayer)-[:HAS_GSTIN]->(tgt)
        
        RETURN id(src) AS source_id, labels(src)[0] AS source_label, 
               src.name AS src_node_name, src_t.name AS src_taxpayer_name, properties(src) AS source_props,
               id(tgt) AS target_id, labels(tgt)[0] AS target_label, 
               tgt.name AS tgt_node_name, tgt_t.name AS tgt_taxpayer_name, properties(tgt) AS target_props,
               rel_type
        """
        results = list(session.run(query))
        
        nodes_dict = {}
        links = []
        
        # We also run reconciliation to tag high risk nodes
        recon_data = run_reconciliation()
        risk_map = {
            m["invoice_id"]: {
                "risk_level": m["risk_level"],
                "root_cause": m["root_cause"]
            } for m in recon_data["mismatches"]
        }
        
        for record in results:
            src_id = str(record["source_id"])
            tgt_id = str(record["target_id"])
            
            src_props = record["source_props"]
            tgt_props = record["target_props"]
            
            # Use source names
            src_node_name = record["src_node_name"]
            src_taxpayer_name = record["src_taxpayer_name"]
            
            # Use target names
            tgt_node_name = record["tgt_node_name"]
            tgt_taxpayer_name = record["tgt_taxpayer_name"]
            
            # Format source node
            if src_id not in nodes_dict:
                # Prioritize Taxpayer Name for GSTIN nodes
                name = src_taxpayer_name or src_node_name or src_props.get("name") or src_props.get("gstin") or src_id
                # If it's a GSTIN node and we have a taxpayer name, clarify both
                if record["source_label"] == "GSTIN" and src_taxpayer_name:
                    src_props["legal_name"] = src_taxpayer_name
                
                risk = "none"
                if record["source_label"] == "Invoice":
                    inv_name = src_props.get("invoice_id") or name
                    r_info = risk_map.get(inv_name, {"risk_level": "Low Risk", "root_cause": "Clean"})
                    risk = r_info["risk_level"].lower().replace(" risk", "")
                    src_props["risk_level"] = r_info["risk_level"]
                    src_props["root_cause"] = r_info["root_cause"]
                
                nodes_dict[src_id] = {"id": src_id, "label": record["source_label"], "name": name, "risk": risk, **src_props}
                
            # Format target node
            if tgt_id not in nodes_dict:
                # Prioritize Taxpayer Name for GSTIN nodes
                name = tgt_taxpayer_name or tgt_node_name or tgt_props.get("name") or tgt_props.get("gstin") or tgt_id
                # If it's a GSTIN node and we have a taxpayer name, clarify both
                if record["target_label"] == "GSTIN" and tgt_taxpayer_name:
                    tgt_props["legal_name"] = tgt_taxpayer_name
                    
                risk = "none"
                if record["target_label"] == "Invoice":
                    inv_name = tgt_props.get("invoice_id") or name
                    r_info = risk_map.get(inv_name, {"risk_level": "Low Risk", "root_cause": "Clean"})
                    risk = r_info["risk_level"].lower().replace(" risk", "")
                    tgt_props["risk_level"] = r_info["risk_level"]
                    tgt_props["root_cause"] = r_info["root_cause"]
                    
                nodes_dict[tgt_id] = {"id": tgt_id, "label": record["target_label"], "name": name, "risk": risk, **tgt_props}
                
            # Format link
            links.append({
                "source": src_id,
                "target": tgt_id,
                "label": record["rel_type"]
            })
            
        return {"nodes": list(nodes_dict.values()), "links": links}

@app.get("/reconciliation")
def reconciliation():
    return run_reconciliation()