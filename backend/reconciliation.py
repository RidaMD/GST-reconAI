# reconciliation.py
from graph import driver

def find_multi_hop_mismatches(tx):
    """
    Traverses invoices and calculates risk based on the exact user-provided matrix:
    1. Structural Risk (Missing IRN, Not in GSTR1/2B, ITC without upstream)
    2. Behavioral Risk (Supplier delays, missing upstream chains)
    3. Financial Exposure (Multiplier based on percent of max invoice size)
    """
    
    # First get the max invoice amount in the dataset for the financial multiplier
    max_amt_query = "MATCH (i:Invoice) RETURN max(i.amount) as max_amt"
    max_amt = tx.run(max_amt_query).single()["max_amt"] or 1.0

    query = """
    MATCH (s:GSTIN)-[:ISSUED]->(i:Invoice)-[:BILLED_TO]->(b:GSTIN)
    OPTIONAL MATCH (t:Taxpayer)-[:HAS_GSTIN]->(s)
    
    OPTIONAL MATCH (i)-[:REPORTED_IN]->(r1:GSTR1)
    OPTIONAL MATCH (pr:PurchaseRegister)-[:RECORDS]->(i)
    OPTIONAL MATCH (i)-[:REFLECTED_IN]->(r2b:GSTR2B)
    OPTIONAL MATCH (i)-[:CLAIMED_IN]->(r3b:GSTR3B)
    
    // Upstream behavioral check
    OPTIONAL MATCH (upstream_inv:Invoice)-[:BILLED_TO]->(s)
    WHERE NOT EXISTS((upstream_inv)-[:REPORTED_IN]->(:GSTR1))
    
    // Historical Risk
    OPTIONAL MATCH (s)-[:ISSUED]->(other_inv:Invoice)
    WHERE other_inv <> i
    OPTIONAL MATCH (other_inv)-[:REPORTED_IN]->(other_r1:GSTR1)
    
    WITH i, s, b, r1, pr, r2b, r3b, t, 
         count(DISTINCT upstream_inv) AS risky_upstream_invoices,
         count(DISTINCT CASE WHEN other_r1 IS NULL THEN other_inv END) AS historical_defects
    
    RETURN i.invoice_id AS invoice_id,
           t.name AS supplier_name,
           i.supplier_gstin AS supplier_gstin,
           b.gstin AS buyer_gstin,
           i.amount AS amount_invoice,
           i.gst_amount AS gst_invoice,
           coalesce(i.gst_claimed, CASE WHEN r3b IS NOT NULL THEN i.gst_amount ELSE 0 END) AS gst_claimed,
           r1.filing_status AS supplier_filing_status,
           r1.delay_days AS supplier_delay_days,
           CASE WHEN r1 IS NULL THEN false ELSE true END AS is_in_gstr1,
           CASE WHEN r2b IS NULL THEN false ELSE true END AS is_in_gstr2b,
           CASE WHEN pr IS NULL THEN false ELSE true END AS is_in_pr,
           'eInvoice' IN labels(i) AS has_irn,
           CASE WHEN i.irn_generated THEN true ELSE false END AS irn_flag,
           risky_upstream_invoices,
           historical_defects
    ORDER BY i.invoice_id ASC
    LIMIT 1000
    """
    results = []
    
    for record in tx.run(query):
        sp = 0 # Structural Points
        bp = 0 # Behavioral Points
        reasons = []
        
        gst_invoice = record["gst_invoice"] or 0
        gst_claimed = record["gst_claimed"] or 0
        amount = record["amount_invoice"] or 0
        
        # --- A. User-Specific "Flag" Logic (from screenshot) ---
        is_filed = record["is_in_gstr1"]
        
        if not is_filed:
            reasons.append("Return Not Filed")
            sp += 60
        
        if gst_claimed > gst_invoice:
            reasons.append("Excess ITC Claim")
            sp += 70
        elif gst_claimed < gst_invoice:
            reasons.append("GST Under-Claim")
            sp += 20
        elif gst_claimed == gst_invoice and is_filed:
            # If everything else is clean, we'll mark as Match later
            pass
        else:
            # gst equals but maybe not filed or other issues
            if is_filed and gst_claimed == gst_invoice:
                pass # placeholder
            
        # Add "GST Mismatch" if values differ at all (general tag)
        if abs(gst_invoice - gst_claimed) > 0.01:
            if "GST Mismatch" not in reasons:
                reasons.append("GST Mismatch")
            sp += 30

        # --- B. Standard Structural Risk Matrix (Fallback/Extra) ---
        if not record["has_irn"] and record["irn_flag"] == False:
            sp += 50
            if "NO IRN" not in reasons: reasons.append("NO IRN")
            
        if not record["is_in_gstr2b"] and not record["is_in_gstr1"]:
            sp += 40
            if "MISSING 2B" not in reasons: reasons.append("MISSING 2B")
            
        # --- C. Vendor Behavioral Risk Matrix ---
        delay = record["supplier_delay_days"] or 0
        if delay > 0 and delay <= 15:
            bp += 10
            reasons.append("LATE FILING")
        elif delay > 15:
            bp += 20
            reasons.append("CHRONIC LATE")
            
        if record["risky_upstream_invoices"] > 0:
            bp += 30
            reasons.append("BROKEN UPSTREAM")

        # --- D. Historical Risk Penalty ---
        historical_defects = record["historical_defects"] or 0
        if historical_defects > 0:
            penalty = min(historical_defects * 20, 100)
            bp += penalty
            reasons.append(f"REPEAT OFFENDER ({historical_defects})")
            
        # --- E. Financial Exposure Multiplier ---
        perc = amount / max_amt
        multiplier = 1.0
        if perc < 0.20: multiplier = 1.0
        elif perc <= 0.50: multiplier = 1.2
        elif perc <= 0.80: multiplier = 1.5
        else: multiplier = 1.8
            
        # --- Final Calculation ---
        total_risk = (sp + bp) * multiplier
        
        # Classification
        if total_risk <= 40: category = "LOW"
        elif total_risk <= 80: category = "MEDIUM"
        elif total_risk <= 130: category = "HIGH"
        else: category = "CRITICAL"
        
        # Default "Match" if clean
        if not reasons:
            reasons.append("Match")
            category = "LOW"
            total_risk = 0

        results.append({
            "invoice_id": record["invoice_id"],
            "supplier_name": record["supplier_name"] or "Unknown Vendor",
            "supplier_gstin": record["supplier_gstin"],
            "buyer_gstin": record["buyer_gstin"],
            "amount_invoice": amount,
            "gst_invoice": gst_invoice,
            "gst_paid": gst_claimed,
            "risk_score": round(total_risk, 2),
            "risk_level": category,
            "root_cause": " | ".join(reasons),
        })
    return results
    return results

def get_mismatches():
    with driver.session() as session:
        return session.execute_read(find_multi_hop_mismatches)