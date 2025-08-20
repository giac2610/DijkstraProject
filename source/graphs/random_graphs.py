
import networkx as nx
import random

class Random_Graph:
    
    def __init__(self, node_num, density, seed):
        number_of_nodes = node_num
        graph_density = density
        graph_seed = seed
        self.graph = self._generate(number_of_nodes,graph_density, graph_seed)

    def _generate(self, node_number, density, seed):
        """
        Purpose: generate random graph with node_number nodes, with graph_Density and a known seed
        """
        # Generate a random graph 
        G = nx.gnp_random_graph(node_number, density, seed=seed)
        # Pesi casuali agli archi
        for u, v in G.edges():
            G[u][v]['weight'] = random.randint(1, 10)
        return G
        

    def get_random_node(self, start_node=None):
        if start_node is not None:
            node = start_node
            while node == start_node:
                node = random.choice(list(self.graph.nodes()))
            return node
        return random.choice(list(self.graph.nodes()))

    def plot_graph(self):
        import matplotlib.pyplot as plt
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', node_size=50, font_size=5, font_color='black')
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.title("Random Graph")
        plt.show()

    def test(self):
        print("Bravo hai dichiarato l'oggetto albero")

