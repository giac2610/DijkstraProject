
import igraph as ig #type: ignore
import random

class Random_Graph:
    
    def __init__(self, node_num, density, seed):
        self.graph = self._generate(node_num,density, seed)

    def _generate(self, node_number, density, seed):
        """
        Purpose: generate random graph with node_number nodes, with graph_Density and a known seed
        """
        random.seed(seed)
        # Generate a random graph 
        G = ig.Graph.Erdos_Renyi(n=node_number, p=density)
        
        # Pesi casuali agli archi
        G.es['weight'] = [random.randint(1, 10) for _ in G.es]
        
        return G
        

    def get_random_node(self, start_node=None):
        if start_node is not None:
            node = start_node
            while node == start_node:
                node = random.choice(range(self.graph.vcount()))
            return node
        return random.choice(range(self.graph.vcount()))

    def plot_graph(self):
        layout = self.graph.layout("kk")
        ig.plot(self.graph, layout=layout, vertex_label=range(self.graph.vcount()))

    def test(self):
        print("Bravo hai dichiarato l'oggetto albero")

