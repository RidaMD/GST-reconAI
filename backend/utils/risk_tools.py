# risk_tools.py
# Extra risk utilities (currently minimal, can expand later)

def classify_risk(diff):
    if diff == 0:
        return "No Risk"
    elif diff <= 50:
        return "Low Risk"
    elif diff <= 200:
        return "Medium Risk"
    else:
        return "High Risk"