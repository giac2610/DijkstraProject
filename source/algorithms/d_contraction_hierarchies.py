import time
import sys

from utils.utils import RawData

class Contraction_Hierarchies:
     def __init__(self):
          self.graph = None
          self.num_queries = 0
          self.results = []
          self.dataUtils = RawData()
     
     def run(self, graph, num_queries, start_node_list, end_node_list):
          pass

     def _node_degree_priority(self):
          # Restituisce una lista di nodi ordinati per grado crescente
          return sorted(self.graph.nodes, key=lambda n: self.graph.degree(n))

     def _edge_difference_priority(self):
          # Restituisce una lista di nodi ordinati per edge difference crescente
          priorities = {}
          for node in self.graph.nodes:
               neighbors = list(self.graph.neighbors(node))
               original_edges = len(neighbors)
               shortcut_edges = 0
               # Conta scorciatoie necessarie tra i vicini
               for i in range(len(neighbors)):
                    for j in range(i+1, len(neighbors)):
                         u, v = neighbors[i], neighbors[j]
                    if not self.graph.has_edge(u, v):
                         shortcut_edges += 1
               priorities[node] = shortcut_edges - original_edges
          return sorted(priorities, key=lambda n: priorities[n])

     def _ch_algotithm(self):
          pass

     def _save_results_to_csv(self):
          self.dataUtils.save_to_csv('ch_results.csv',self.results)