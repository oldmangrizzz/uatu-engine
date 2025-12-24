"""
Graph generation for visualizing multiversal history as a DAG.
"""
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


class MultiversalGraphGenerator:
    """Generates a directed acyclic graph (DAG) of character's multiversal history."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def build_graph(self, character_profile: Dict[str, Any]) -> nx.DiGraph:
        """Build a DAG from character profile data."""
        logger.info(f"Building graph for {character_profile.get('primary_name', 'Unknown')}")
        
        character_name = character_profile.get("primary_name", "Unknown Character")
        
        # Add central character node
        self.graph.add_node(
            character_name,
            node_type="character",
            label=character_name
        )
        
        # Add multiversal identity nodes
        multiversal_identities = character_profile.get("multiversal_identities", [])
        for identity in multiversal_identities:
            universe = identity.get("universe", "Unknown Universe")
            node_id = f"{character_name}_{universe}"
            self.graph.add_node(
                node_id,
                node_type="universe",
                label=universe
            )
            self.graph.add_edge(character_name, node_id, relationship="exists_in")
        
        # Add knowledge domain nodes
        knowledge_domains = character_profile.get("knowledge_domains", [])
        for idx, domain in enumerate(knowledge_domains):
            domain_id = f"domain_{idx}_{domain.get('category', 'unknown')}"
            self.graph.add_node(
                domain_id,
                node_type="knowledge",
                label=f"{domain.get('category', 'Unknown')}\n{domain.get('proficiency_level', '')}",
                earth_equivalent=domain.get("earth_1218_equivalent", "")
            )
            self.graph.add_edge(character_name, domain_id, relationship="possesses")
        
        # Add economic event nodes
        economic_history = character_profile.get("economic_history", [])
        for idx, event in enumerate(economic_history):
            event_id = f"economic_{idx}"
            event_label = event.get("event_type", "economic_event")
            amount = event.get("amount", 0)
            self.graph.add_node(
                event_id,
                node_type="economic",
                label=f"{event_label}\n${amount:,.0f}" if amount else event_label,
                description=event.get("description", "")[:50]
            )
            self.graph.add_edge(character_name, event_id, relationship="participated_in")
        
        # Add wealth node if available
        total_wealth = character_profile.get("total_wealth_estimate")
        if total_wealth:
            wealth_node = "total_wealth"
            self.graph.add_node(
                wealth_node,
                node_type="wealth",
                label=f"Total Wealth\n${total_wealth:,.0f}"
            )
            self.graph.add_edge(character_name, wealth_node, relationship="possesses")
        
        logger.info(f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
        return self.graph
    
    def visualize(self, output_path: str = "multiversal_history_graph.png", title: str = "Multiversal History") -> str:
        """Visualize the graph and save to file."""
        logger.info(f"Visualizing graph to {output_path}")
        
        if self.graph.number_of_nodes() == 0:
            logger.warning("Graph is empty, nothing to visualize")
            return ""
        
        # Set up the plot
        plt.figure(figsize=(16, 12))
        
        # Use hierarchical layout
        try:
            pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
        except Exception as e:
            logger.warning(f"Spring layout failed, using circular layout: {e}")
            pos = nx.circular_layout(self.graph)
        
        # Define colors for different node types
        color_map = {
            "character": "#FF6B6B",  # Red
            "universe": "#4ECDC4",   # Teal
            "knowledge": "#95E1D3",  # Light teal
            "economic": "#FFE66D",   # Yellow
            "wealth": "#FF9F1C"      # Orange
        }
        
        # Get node colors based on type
        node_colors = []
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get("node_type", "unknown")
            node_colors.append(color_map.get(node_type, "#CCCCCC"))
        
        # Get node labels
        labels = {}
        for node in self.graph.nodes():
            labels[node] = self.graph.nodes[node].get("label", node)
        
        # Draw the graph
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_color=node_colors,
            node_size=3000,
            alpha=0.9
        )
        
        nx.draw_networkx_labels(
            self.graph, pos,
            labels,
            font_size=8,
            font_weight="bold"
        )
        
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color="#888888",
            arrows=True,
            arrowsize=20,
            arrowstyle="->",
            width=2,
            alpha=0.6
        )
        
        plt.title(title, fontsize=20, fontweight="bold", pad=20)
        plt.axis("off")
        plt.tight_layout()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Save the figure
        plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close()
        
        logger.info(f"Graph visualization saved to {output_path}")
        return output_path
    
    def export_to_gexf(self, output_path: str = "multiversal_history.gexf") -> str:
        """Export graph to GEXF format for use in other tools like Gephi."""
        logger.info(f"Exporting graph to GEXF format: {output_path}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        nx.write_gexf(self.graph, output_path)
        logger.info(f"Graph exported to {output_path}")
        return output_path
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph."""
        if self.graph.number_of_nodes() == 0:
            return {"error": "Graph is empty"}
        
        stats = {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "is_dag": nx.is_directed_acyclic_graph(self.graph),
            "node_types": {}
        }
        
        # Count nodes by type
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get("node_type", "unknown")
            stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1
        
        return stats
