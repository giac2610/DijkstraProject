from graphs.graph_interface import GraphInterface
import operator
import osmnx as ox
import networkx as nx
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

weight = "length"

class RealGraph(GraphInterface):
     
     def __init__(self):
          
          # create networkx graph
          place = "L'Aquila, Abruzzo, Italy"
          G_nx = ox.graph.graph_from_place(place, network_type="drive")
          gdf = ox.geocoder.geocode_to_gdf(place)
          osmids = list(G_nx.nodes)
          G_nx = nx.relabel.convert_node_labels_to_integers(G_nx)

          # plot the network, but do not show it or close it yet
          fig, ax = ox.plot.plot_graph(
               G_nx,
               show=False,
               close=False,
               bgcolor="#111111",
               edge_color="#ffcb00",
               edge_linewidth=0.3,
               node_size=0,
          )

          # to this matplotlib axis, add the place shape(s)
          gdf.plot(ax=ax, fc="#444444", ec=None, lw=1, alpha=1, zorder=-1)

          # optionally set up the axes extents
          margin = 0.02
          west, south, east, north = gdf.union_all().bounds
          margin_ns = (north - south) * margin
          margin_ew = (east - west) * margin
          ax.set_ylim((south - margin_ns, north + margin_ns))
          ax.set_xlim((west - margin_ew, east + margin_ew))
          plt.show()
          # give each node its original osmid as attribute since we relabeled them
          osmid_values = dict(zip(G_nx.nodes, osmids))
          nx.set_node_attributes(G_nx, osmid_values, "osmid")
          
          G_ig = ig.Graph(directed=True)
          G_ig.add_vertices(G_nx.nodes)
          G_ig.add_edges(G_nx.edges())
          G_ig.vs["osmid"] = osmids
          G_ig.es[weight] = list(nx.get_edge_attributes(G_nx, weight).values())

     def _generate(self):
          pass
     
     def get_random_node(self, start_node=None):
          pass
     
     def plot_graph(self):
          pass