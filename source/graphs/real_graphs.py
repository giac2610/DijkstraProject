from graphs.graph_interface import GraphInterface
import osmnx as ox
import networkx as nx
import igraph as ig
import matplotlib.pyplot as plt
import random

class RealGraph(GraphInterface):
     
    def __init__(self, place_name="L'Aquila, Abruzzo, Italy"):
        self.place_name = place_name
        self.graph, self.G_nx, self.gdf, self.node_to_osmid, self.G_nx_orig_plot = self._generate()

    def _generate(self):
        print(f"Download dei dati stradali per: {self.place_name}...")
        
        # Scarichiamo il grafo con osmid come etichette dei nodi
        G_nx_orig = ox.graph.graph_from_place(self.place_name, network_type="drive")
        
        # Creiamo le mappe di conversione da osmid a indice intero e viceversa
        self.node_to_osmid = {i: osmid for i, osmid in enumerate(G_nx_orig.nodes())}
        
        # Rinominiamo i nodi del grafo networkx in interi per compatibilità con igraph
        G_nx_reindexed = nx.relabel.convert_node_labels_to_integers(G_nx_orig)
        
        gdf = ox.geocoder.geocode_to_gdf(self.place_name)
        
        G_nx_reindexed = ox.add_edge_speeds(G_nx_reindexed)
        G_nx_reindexed = ox.add_edge_travel_times(G_nx_reindexed)
        
        # Creiamo il grafo igraph
        G_ig = ig.Graph.from_networkx(G_nx_reindexed, create_using=nx.DiGraph)
        G_ig.es['weight'] = G_ig.es['travel_time']
        
        # Conserviamo il grafo networkx originale (con osmid) solo per il plotting
        G_nx_orig_plot = G_nx_orig
        
        return G_ig, G_nx_reindexed, gdf, self.node_to_osmid, G_nx_orig_plot

    def get_random_node(self, start_node=None):
        if start_node is not None:
            node = start_node
            while node == start_node:
                node = random.choice(range(self.graph.vcount()))
            return node
        return random.choice(range(self.graph.vcount()))

    def plot_graph(self, path=None, start_node=None, end_node=None):
        """
        Visualizza il grafo. 
        - Se viene fornito un 'path' (lista di indici di nodi), evidenzia quel percorso.
        - Se vengono forniti 'start_node' e 'end_node', evidenzia i punti di inizio e fine.
        """
        nodes_to_color = []
        if start_node is not None and start_node in self.node_to_osmid:
            nodes_to_color.append(self.node_to_osmid.get(start_node))
        if end_node is not None and end_node in self.node_to_osmid:
            nodes_to_color.append(self.node_to_osmid.get(end_node))

        # Colora i nodi di partenza/arrivo e rendili visibili
        node_colors = ['green' if node in nodes_to_color else '#111111' for node in self.G_nx_orig_plot.nodes()]
        node_sizes = [50 if node in nodes_to_color else 0 for node in self.G_nx_orig_plot.nodes()]

        if path and isinstance(path, list) and len(path) > 1:
            # Convertiamo i nostri indici interni di nuovo in OSMID, che osmnx capisce
            osmid_path = [self.node_to_osmid[node_idx] for node_idx in path if node_idx in self.node_to_osmid]
            
            if len(osmid_path) < 2:
                print("Percorso troppo corto per essere visualizzato.")
                ox.plot_graph(self.G_nx_orig_plot, node_size=node_sizes, node_color=node_colors, edge_linewidth=0.5, bgcolor="#111111", edge_color="w")
                return
            
            print("Visualizzazione del grafo con percorso evidenziato...")
            # Usiamo la funzione di osmnx per plottare il grafo con il percorso
            ox.plot_graph_route(self.G_nx_orig_plot, osmid_path, route_color='r', route_linewidth=4, 
                                node_size=node_sizes, node_color=node_colors, bgcolor="#111111", edge_color="w")
        else:
            print("Visualizzazione del grafo (senza percorso specificato)...")
            ox.plot_graph(self.G_nx_orig_plot, node_size=node_sizes, node_color=node_colors, edge_linewidth=0.5, bgcolor="#111111", edge_color="w")

