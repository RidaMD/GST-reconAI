# graph_tools.py
from graph import driver

def run_query(query, parameters=None):
    with driver.session() as session:
        return session.run(query, parameters or {})