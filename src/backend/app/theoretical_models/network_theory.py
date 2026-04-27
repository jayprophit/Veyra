"""Network Theory Models for Market Analysis"""
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Node:
    id: str
    type: str
    connections: List[str]
    weight: float

class NetworkTheoryAnalyzer:
    """Analyze market networks and connections"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
    
    def build_correlation_network(self, correlations: Dict[Tuple[str, str], float]) -> Dict:
        """Build network from correlation data"""
        # Build adjacency list
        for (asset1, asset2), corr in correlations.items():
            if abs(corr) > 0.7:  # Strong correlation threshold
                self.adjacency[asset1].append(asset2)
                self.adjacency[asset2].append(asset1)
        
        # Calculate network metrics
        metrics = self._calculate_network_metrics()
        
        return {
            "nodes": len(self.adjacency),
            "edges": sum(len(v) for v in self.adjacency.values()) // 2,
            "density": metrics["density"],
            "clusters": metrics["clusters"],
            "central_assets": metrics["central"],
            "implication": "High clustering suggests contagion risk"
        }
    
    def _calculate_network_metrics(self) -> Dict:
        """Calculate network metrics"""
        n = len(self.adjacency)
        if n == 0:
            return {"density": 0, "clusters": 0, "central": []}
        
        # Density
        possible_edges = n * (n - 1) / 2
        actual_edges = sum(len(v) for v in self.adjacency.values()) / 2
        density = actual_edges / possible_edges if possible_edges > 0 else 0
        
        # Degree centrality
        degrees = {node: len(connections) for node, connections in self.adjacency.items()}
        max_degree = max(degrees.values()) if degrees else 1
        centrality = {node: deg / max_degree for node, deg in degrees.items()}
        
        # Most central nodes
        central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "density": round(density, 3),
            "clusters": self._detect_clusters(),
            "central": [{"asset": k, "centrality": round(v, 3)} for k, v in central]
        }
    
    def _detect_clusters(self) -> int:
        """Detect number of clusters using simple connected components"""
        visited = set()
        clusters = 0
        
        def dfs(node):
            visited.add(node)
            for neighbor in self.adjacency.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
        
        for node in self.adjacency:
            if node not in visited:
                dfs(node)
                clusters += 1
        
        return clusters
    
    def find_contagion_path(self, source: str, target: str, max_depth: int = 3) -> Dict:
        """Find contagion path between assets"""
        # BFS
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            current, path = queue.pop(0)
            
            if current == target:
                return {
                    "path_exists": True,
                    "path": path,
                    "length": len(path) - 1,
                    "contagion_risk": "HIGH" if len(path) <= 2 else "MEDIUM"
                }
            
            if len(path) >= max_depth:
                continue
            
            for neighbor in self.adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return {
            "path_exists": False,
            "contagion_risk": "LOW"
        }
    
    def calculate_systemic_importance(self, node_id: str) -> Dict:
        """Calculate systemic importance of node"""
        if node_id not in self.adjacency:
            return {"error": "Node not in network"}
        
        # Degree centrality
        degree = len(self.adjacency[node_id])
        
        # Calculate how many paths go through this node (simplified)
        paths_through = 0
        all_nodes = list(self.adjacency.keys())
        
        for source in all_nodes:
            for target in all_nodes:
                if source != target and source != node_id and target != node_id:
                    path = self._shortest_path(source, target)
                    if node_id in path:
                        paths_through += 1
        
        # Betweenness approximation
        n = len(all_nodes)
        max_betweenness = (n - 1) * (n - 2)
        betweenness = paths_through / max_betweenness if max_betweenness > 0 else 0
        
        return {
            "node": node_id,
            "degree_centrality": degree,
            "betweenness_centrality": round(betweenness, 3),
            "systemic_importance": "HIGH" if betweenness > 0.3 else "MEDIUM" if betweenness > 0.1 else "LOW",
            "implication": "Failure would cascade" if betweenness > 0.3 else "Limited contagion risk"
        }
    
    def _shortest_path(self, source: str, target: str) -> List[str]:
        """Find shortest path using BFS"""
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            current, path = queue.pop(0)
            if current == target:
                return path
            
            for neighbor in self.adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def detect_network_anomaly(self, baseline: Dict, current: Dict) -> Dict:
        """Detect anomalies in network structure"""
        anomalies = []
        
        # Check for new edges (new correlations)
        baseline_edges = set(baseline.get("edges", []))
        current_edges = set(current.get("edges", []))
        
        new_edges = current_edges - baseline_edges
        removed_edges = baseline_edges - current_edges
        
        if len(new_edges) > len(baseline_edges) * 0.1:
            anomalies.append("Significant new correlations forming - possible regime change")
        
        if len(removed_edges) > len(baseline_edges) * 0.1:
            anomalies.append("Many correlations breaking - decoupling event")
        
        # Check density change
        density_change = abs(current.get("density", 0) - baseline.get("density", 0))
        if density_change > 0.2:
            anomalies.append(f"Network density changed significantly ({density_change:.2f})")
        
        return {
            "anomalies_detected": len(anomalies),
            "anomaly_list": anomalies,
            "severity": "HIGH" if len(anomalies) > 2 else "MEDIUM" if anomalies else "LOW",
            "recommendation": "Review portfolio correlations" if anomalies else "No action needed"
        }
