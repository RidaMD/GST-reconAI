import requests
from collections import Counter

try:
    response = requests.get("http://localhost:8000/mismatches")
    data = response.json()
    
    levels = [m['risk_level'] for m in data]
    print(f"Risk Level Distribution: {Counter(levels)}")
    
    causes = []
    for m in data:
        causes.extend(m['root_cause'].split(' | '))
    print(f"Top 10 Risk Causes: {Counter(causes).most_common(10)}")

except Exception as e:
    print(f"Error: {e}")
