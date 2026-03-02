import requests
from collections import defaultdict

def test_connectivity():
    try:
        response = requests.get('http://localhost:8001/graph-data')
        data = response.json()
        nodes = data.get("nodes", [])
        links = data.get("links", [])
        
        print(f"Total nodes: {len(nodes)}")
        print(f"Total links: {len(links)}")
        
        adjacency = defaultdict(set)
        for link in links:
            source = link['source']
            target = link['target']
            # source could be dict if force-graph has modified it, but usually its string here
            if isinstance(source, dict):
                source = source['id']
            if isinstance(target, dict):
                target = target['id']
            adjacency[source].add(target)
            adjacency[target].add(source)
            
        degrees = [len(v) for v in adjacency.values()]
        if degrees:
            print(f"Min degree: {min(degrees)}")
            print(f"Max degree: {max(degrees)}")
            print(f"Avg degree: {sum(degrees)/len(degrees)}")
            print(f"Number of nodes with degree > 50: {sum(1 for d in degrees if d > 50)}")
        
        # Check if all nodes are actually connected to all others
        n = len(nodes)
        if n > 0:
            possible_edges = n * (n - 1) / 2
            print(f"Density: {len(links) / possible_edges}")
            
        # Lets see what nodes have max degree
        for node in nodes:
            deg = len(adjacency[node['id']])
            if deg > 50:
                print(f"Hub node: {node['label']} {node.get('name', '')} (id: {node['id']}) - degree: {deg}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connectivity()
