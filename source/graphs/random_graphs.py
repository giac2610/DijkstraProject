
import igraph as ig #type: ignore
import random
from graphs.graph_interface import GraphInterface

class Random_Graph(GraphInterface):
    
    def __init__(self, node_num, density, seed):
        self.graph = self._generate(node_num,density, seed)

    def _generate(self, node_number, density, seed):
        random.seed(seed)
        
        # Calcoliamo i parametri per Watts-Strogatz
        # k è il grado medio di ciascun nodo (numero di vicini)
        # Assumiamo che ogni nodo sia connesso ai suoi k/2 vicini più prossimi
        k = int(node_number * density)
        if k < 2: k = 2
        
        # p è la probabilità di "rewiring" di un arco
        p = 0.1

        print(f"Generating Watts-Strogatz graph with n={node_number}, k={k}, p={p}")
        
        G = ig.Graph.Watts_Strogatz(dim=1, size=node_number, nei=k, p=p)
        
        # Rendiamo il grafo diretto per coerenza con il grafo reale
        G.to_directed()
        
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


