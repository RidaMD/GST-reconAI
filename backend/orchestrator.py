# orchestrator.py
from reconciliation import get_mismatches
from utils.audit_tools import summarize_risks

def run_reconciliation():
    mismatches = get_mismatches()
    summary = summarize_risks(mismatches)
    
    # Count root-cause types dynamically
    root_cause_summary = {}
    for m in mismatches:
        rc = m["root_cause"]
        if rc not in root_cause_summary:
            root_cause_summary[rc] = 0
        root_cause_summary[rc] += 1
    
    return {
        "mismatches": mismatches,
        "risk_summary": summary,
        "root_cause_summary": root_cause_summary
    }