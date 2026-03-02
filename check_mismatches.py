import requests
import json

try:
    response = requests.get("http://localhost:8000/mismatches")
    data = response.json()
    
    print(f"Total records returned: {len(data)}")
    
    clean_count = sum(1 for m in data if "Clean" in m['root_cause'])
    print(f"Clean (transactional) records: {clean_count}")
    
    # Print first 2 records for verification
    print("\nSample records:")
    print(json.dumps(data[:2], indent=2))
    
except Exception as e:
    print(f"Error: {e}")
