# test_fastapi.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_reconciliation_endpoint():
    response = client.get("/reconciliation")
    assert response.status_code == 200

    data = response.json()
    # Check main keys
    assert "mismatches" in data
    assert "risk_summary" in data
    assert "root_cause_summary" in data

    # Check at least one mismatch has all required fields
    if data["mismatches"]:
        m = data["mismatches"][0]
        required_fields = [
            "invoice_id", "supplier_gstin", "buyer_gstin", 
            "amount_invoice", "gst_invoice", "gst_paid",
            "risk_level", "root_cause", "downstream_chain"
        ]
        for field in required_fields:
            assert field in m