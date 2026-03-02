import os
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def clear_db(tx):
    query = """
    MATCH (n)
    WITH n LIMIT 1000
    DETACH DELETE n
    RETURN count(n) as d
    """
    total_deleted = 0
    while True:
        result = tx.run(query)
        deleted = result.single()["d"]
        total_deleted += deleted
        if deleted == 0:
            break
    print(f"Deleted {total_deleted} existing nodes.")

def ingest_from_csv(tx):
    # Check for consolidated mock data first
    # If running from root: gst_reconciliation_mock_data.csv
    # If running from backend/: ../gst_reconciliation_mock_data.csv
    consolidated_path = "gst_reconciliation_mock_data.csv" if os.path.exists("gst_reconciliation_mock_data.csv") else "../gst_reconciliation_mock_data.csv"
    if os.path.exists(consolidated_path):
        print(f"Detected consolidated mock data: {consolidated_path}")
        df = pd.read_csv(consolidated_path)
        
        # Clean column names (strip spaces if any)
        df.columns = [c.strip() for c in df.columns]
        
        for _, row in df.iterrows():
            inv_id = str(row['Invoice_ID'])
            s_gstin = str(row['Supplier_GSTIN'])
            b_gstin = str(row['Buyer_GSTIN'])
            amount = float(row['Invoice_Amount'])
            gst_s = float(row['GST_As_Per_Supplier'])
            gst_b = float(row['GST_Claimed_By_Buyer'])
            filed = str(row['Return_Filed']).lower() == 'yes'
            
            # 1. Create Taxpayers (Generic placeholders since consolidated doesn't have them)
            tx.run("MERGE (t:Taxpayer {taxpayer_id: $tid}) ON CREATE SET t.name = $name", 
                   tid="T-"+s_gstin, name="Supplier_"+s_gstin)
            tx.run("MERGE (t:Taxpayer {taxpayer_id: $tid}) ON CREATE SET t.name = $name", 
                   tid="T-"+b_gstin, name="Buyer_"+b_gstin)
            
            # 2. Create GSTINs and link
            tx.run("""
                MATCH (t:Taxpayer {taxpayer_id: $tid})
                MERGE (g:GSTIN {gstin: $gstin})
                MERGE (t)-[:HAS_GSTIN]->(g)
            """, tid="T-"+s_gstin, gstin=s_gstin)
            tx.run("""
                MATCH (t:Taxpayer {taxpayer_id: $tid})
                MERGE (g:GSTIN {gstin: $gstin})
                MERGE (t)-[:HAS_GSTIN]->(g)
            """, tid="T-"+b_gstin, gstin=b_gstin)
            
            # 3. Create Returns
            if filed:
                tx.run("""
                    MATCH (g:GSTIN {gstin: $gstin})
                    MERGE (r:GSTR1 {return_id: $rid, month: '2024-06', filing_status: 'Filed'})
                    MERGE (g)-[:FILED_ON_TIME]->(r)
                """, gstin=s_gstin, rid="R1-"+inv_id)
            
            # 4. Create Invoice
            tx.run("""
                MATCH (s:GSTIN {gstin: $sg})
                MATCH (b:GSTIN {gstin: $bg})
                CREATE (i:Invoice:eInvoice {
                    invoice_id: $inv_id,
                    supplier_gstin: $sg,
                    buyer_gstin: $bg,
                    amount: $amt,
                    gst_amount: $gst_s,
                    gst_claimed: $gst_b,
                    date: '2024-06-15',
                    irn_generated: true
                })
                CREATE (s)-[:ISSUED]->(i)
                CREATE (i)-[:BILLED_TO]->(b)
            """, inv_id=inv_id, sg=s_gstin, bg=b_gstin, amt=amount, gst_s=gst_s, gst_b=gst_b)
            
        print("Consolidated data ingestion complete.")
        return

    # Fallback to standard split files
    base_dir = "../mock data"
    if not os.path.exists(os.path.join(base_dir, "taxpayers.csv")):
        print("No mock data files found. Skipping ingestion.")
        return
        
    # 1. Load Taxpayers

    print("CSV data ingestion complete.")

if __name__ == "__main__":
    with driver.session() as session:
        print("Clearing old mock data...")
        session.execute_write(clear_db)
        print("Starting CSV ingestion...")
        session.execute_write(ingest_from_csv)
    driver.close()
