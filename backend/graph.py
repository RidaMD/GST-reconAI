from dotenv import load_dotenv
import os
from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_URI = os.getenv("NEO4J_URI")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_graph(tx):
    # Fetch nodes and relationships separately to include isolated nodes
    nodes_query = "MATCH (n) RETURN n LIMIT 100"
    rels_query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100"

    # Collect nodes
    result_nodes = tx.run(nodes_query)
    nodes = {}
    for record in result_nodes:
        node = record["n"]
        node_id = str(node.id)
        labels = list(node.labels)
        node_label = ','.join(labels) if labels else "NoLabel"
        name = node.get("invoice_id") or node.get("return_id") or node_id
        nodes[node_id] = {"name": name, "label": node_label}

    # Collect relationships
    edges = []
    result_rels = tx.run(rels_query)
    for record in result_rels:
        n = record["n"]
        m = record["m"]
        r = record["r"]

        n_id = str(n.id)
        m_id = str(m.id)

        rel_type = r.type if r else "NoRel"
        edges.append((nodes[n_id]["name"], nodes[m_id]["name"], rel_type))

    return nodes, edges

def draw_graph():
    # Fetch graph data
    with driver.session() as session:
        nodes, edges = session.execute_read(get_graph)

    # Build the graph
    G = nx.DiGraph()
    for node_id, info in nodes.items():
        G.add_node(info["name"], label=info["label"])

    for u, v, rel_type in edges:
        G.add_edge(u, v, label=rel_type)

    # Assign colors based on node label
    color_map = []
    for n in G.nodes(data=True):
        label = n[1]['label']
        if "Invoice" in label:
            color_map.append("skyblue")
        elif "GSTR1" in label:
            color_map.append("lightgreen")
        elif "GSTR3B" in label:
            color_map.append("salmon")
        elif "GSTR2B" in label:
            color_map.append("orange")
        elif "GSTIN" in label:
            color_map.append("purple")
        else:
            color_map.append("grey")

    # Draw the graph
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    labels = {n: f"{n}\n({G.nodes[n].get('label', '')})" for n in G.nodes()}
    nx.draw(
        G, pos,
        with_labels=True,
        labels=labels,
        node_color=color_map,
        node_size=2000,
        arrowstyle='->',
        arrowsize=20
    )
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()

if __name__ == "__main__":
    draw_graph()