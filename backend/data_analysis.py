import pandas as pd
import requests

def analyze():
    print("--- Loading Mock Data ---")
    invoices = pd.read_csv('../mock data/invoices.csv')
    returns = pd.read_csv('../mock data/returns.csv')
    
    print(f"Total Invoices: {len(invoices)}")
    print(f"Total Returns: {len(returns)}")
    
    # Let's assess Expected Behavioral Risks
    # 1. Missed Filing (Supplier Non Filed)
    missed_gstr1 = returns[(returns['type'] == 'GSTR1') & (returns['filing_status'] == 'Not Filed')]
    expected_missed_gstr1 = len(missed_gstr1)
    
    # 2. Let's get actuals from FastAPI
    print("\n--- Fetching Actuals from Knowledge Graph Engine ---")
    response = requests.get('http://localhost:8001/mismatches')
    actual_data = response.json()
    
    print(f"Total Graph Mismatches Triggered: {len(actual_data)}")
    
    # Extract root_cause counts
    root_causes = {}
    for d in actual_data:
        causes = d['root_cause'].split(' | ')
        for c in causes:
            if c:
                root_causes[c] = root_causes.get(c, 0) + 1
    
    print("\n--- Actual Risk Tag Distribution ---")
    for k, v in sorted(root_causes.items(), key=lambda x: x[1], reverse=True):
        print(f"{k}: {v}")
        
    print("\n--- Expected vs Actual Sample Metrics ---")
    print(f"Expected missed GSTR-1 returns from dataset: {expected_missed_gstr1}")
    print(f"Actual tagged 'SUPPLIER NON FILED' or 'MISSED FILING': {root_causes.get('SUPPLIER NON FILED', 0) + root_causes.get('MISSED FILING', 0)}")
    
    # Check "Clean" nodes
    clean_count = root_causes.get('Clean', 0)
    print(f"\nPerfectly Clean Invoices (0 Risk): {clean_count}")
    
    # Ratio
    risk_ratio = 100 - (clean_count / len(invoices) * 100)
    print(f"Graph Risk Ratio: {risk_ratio:.1f}%")

if __name__ == "__main__":
    analyze()
