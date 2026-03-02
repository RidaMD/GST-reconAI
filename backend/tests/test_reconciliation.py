# test_reconciliation.py
from reconciliation import get_mismatches

def test_get_mismatches_structure():
    mismatches = get_mismatches()
    assert isinstance(mismatches, list)
    if mismatches:
        m = mismatches[0]
        fields = [
            "invoice_id", "supplier_gstin", "buyer_gstin",
            "amount_invoice", "gst_invoice", "gst_paid",
            "risk_level", "root_cause", "downstream_chain"
        ]
        for field in fields:
            assert field in m