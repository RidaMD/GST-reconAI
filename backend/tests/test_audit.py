import requests
import json

def generate_sample_audit():
    print("Fetching mismatches...")
    resp = requests.get('http://localhost:8001/mismatches')
    mismatches = resp.json()
    
    high_risk_invoices = [m for m in mismatches if m['risk_level'] in ['CRITICAL', 'HIGH']]
    
    if not high_risk_invoices:
        print("No high risk invoices found.")
        return
        
    # Get the top risk
    top_risk = max(high_risk_invoices, key=lambda x: x['risk_score'])
    inv_id = top_risk['invoice_id']
    
    print(f"Generating AI Audit for top risk invoice: {inv_id} (Score: {top_risk['risk_score']})")
    
    audit_resp = requests.get(f'http://localhost:8001/audit-report/{inv_id}')
    
    if audit_resp.status_code == 200:
        data = audit_resp.json()
        report_md = data.get('report_markdown', 'No markdown returned')
        print("\n" + "="*50)
        print("NLP AUDIT REPORT:")
        print("="*50)
        print(report_md)
        print("="*50)
        
        with open("sample_audit.md", "w") as f:
            f.write(report_md)
    else:
        print(f"Error: {audit_resp.status_code} - {audit_resp.text}")

if __name__ == "__main__":
    generate_sample_audit()
