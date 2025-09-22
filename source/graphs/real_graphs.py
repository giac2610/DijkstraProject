from graphs.graph_interface import GraphInterface
import osmnx as ox
import networkx as nx
import igraph as ig
import matplotlib.pyplot as plt
import random

weight = "length"

class RealGraph(GraphInterface):
     
    def __init__(self):
        self.graph, self.G_nx, self.gdf = self._generate()

    def _generate(self):
        place = "L'Aquila, Abruzzo, Italy"
        
        # Scarica il grafo stradale e il geodataframe del contorno della città
        G_nx = ox.graph.graph_from_place(place, network_type="drive")
        # 1. Aggiunge le velocità stimate in base al tipo di strada
        G_nx = ox.add_edge_speeds(G_nx)
        # 2. Calcola i tempi di percorrenza (lunghezza/velocità)
        G_nx = ox.add_edge_travel_times(G_nx)
        gdf = ox.geocoder.geocode_to_gdf(place)
        
        # Salva gli ID originali di OpenStreetMap (osmid) prima di rinumerare i nodi
        osmids = list(G_nx.nodes)
        
        # Converte le etichette dei nodi da osmid a interi (es. 0, 1, 2, ...) per la compatibilità con igraph
        G_nx_reindexed = nx.relabel.convert_node_labels_to_integers(G_nx)
        
        # Crea un grafo igraph vuoto e aggiunge vertici e archi dal grafo networkx
        G_ig = ig.Graph(directed=True)
        G_ig.add_vertices(G_nx_reindexed.nodes)
        G_ig.add_edges(G_nx_reindexed.edges())
        
        # Assegna gli attributi al grafo igraph
        osmid_mapping = {i: osmid for i, osmid in enumerate(osmids)}
        # Mappa i nuovi indici interi ai loro osmid originali
        G_ig.vs["osmid"] = [osmid_mapping[v.index] for v in G_ig.vs]
        
        # Il nome dell'attributo da osmnx ('length' o 'travel_time')
        source_weight_attribute = "travel_time" 
        # Prendiamo i valori da osmnx usando il suo nome specifico
        edge_weights = nx.get_edge_attributes(G_nx_reindexed, source_weight_attribute).values()
        
        # Assegniamo questi valori all'attributo standard 'weight' che l'algoritmo si aspetta
        G_ig.es['weight'] = list(edge_weights)

        return G_ig, G_nx_reindexed, gdf

    def get_random_node(self, start_node=None):
        if start_node is not None:
            node = start_node
            # Continua a scegliere un nodo finché non ne trova uno diverso da start_node
            while node == start_node:
                node = random.choice(range(self.graph.vcount()))
            return node
        
        # Se non viene fornito start_node, restituisce un qualsiasi nodo casuale
        return random.choice(range(self.graph.vcount()))

    def plot_graph(self):
        fig, ax = ox.plot.plot_graph(
            self.G_nx,
            show=False,
            close=False,
            bgcolor="#111111",
            edge_color="#ffcb00",
            edge_linewidth=0.3,
            node_size=0,
        )

        # Aggiunge il contorno della città (geodataframe) al plot come sfondo
        self.gdf.plot(ax=ax, fc="#444444", ec=None, lw=1, alpha=1, zorder=-1)

        # Imposta i limiti della mappa per una visualizzazione ottimale
        margin = 0.02
        west, south, east, north = self.gdf.union_all().bounds
        margin_ns = (north - south) * margin
        margin_ew = (east - west) * margin
        ax.set_ylim((south - margin_ns, north + margin_ns))
        ax.set_xlim((west - margin_ew, east + margin_ew))
        
        # Mostra il plot a schermo
        plt.show()