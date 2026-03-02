# audit_tools.py
# Optional utilities for auditing invoices or GST data

def summarize_risks(mismatches):
    summary = {"No Risk": 0, "Low Risk": 0, "Medium Risk": 0, "High Risk": 0, "Critical Risk": 0}
    for m in mismatches:
        risk_level = m.get("risk_level", "No Risk")
        if risk_level not in summary:
            summary[risk_level] = 0
        summary[risk_level] += 1
    return summary