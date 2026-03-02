# test_graph.py
from graph_tools import run_query

def test_run_query():
    result = run_query("RETURN 1 AS test")
    records = list(result)
    assert len(records) == 1
    assert records[0]["test"] == 1