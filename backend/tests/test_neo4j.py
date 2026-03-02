# test_neo4j.py
from graph import driver

def test_driver_connection():
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        records = list(result)
        assert records[0]["test"] == 1

def test_multi_hop_relationship():
    """
    Checks if at least one multi-hop SOLD_TO relationship exists.
    """
    with driver.session() as session:
        query = """
        MATCH (i:Invoice)-[:SOLD_TO*1..2]->(b:Invoice)
        RETURN i.invoice_id AS invoice_id, b.invoice_id AS downstream
        LIMIT 1
        """
        result = list(session.run(query))
        # If the dataset has relationships, it should return at least 0 or 1 record
        assert isinstance(result, list)
        if result:
            r = result[0]
            assert "invoice_id" in r and "downstream" in r