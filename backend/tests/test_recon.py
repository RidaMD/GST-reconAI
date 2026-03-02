import traceback
try:
    import reconciliation
    print(len(reconciliation.get_mismatches()))
except Exception as e:
    traceback.print_exc()
