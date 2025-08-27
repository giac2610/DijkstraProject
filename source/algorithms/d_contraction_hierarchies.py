import time
import sys
import heapq
import networkx as nx

from utils.utils import RawData

class Contraction_Hierarchies:
    def __init__(self, graph=None):
        self.original_graph = graph
        self.dataUtils = RawData()
        
        self.shortcut_graph = None
        self.node_order = None
        self.node_levels = None
        self.preprocessing_time = 0.0
        self.space_preprocessing_bytes = 0

    def preprocess(self):
         
          start_time = time.time()
          
          graph = self.original_graph.copy()
          
          priority_queue = []
          
          initial_priorities = {node: self._calculate_priority(graph, node) for node in graph.nodes()}
          for node, priority in initial_priorities.items():
               heapq.heappush(priority_queue, (priority, node))
               
          self.node_order = []
          self.node_levels = {}
          processed_nodes = set()

          while priority_queue:
               
               priority, node = heapq.heappop(priority_queue)

               current_priority = self._calculate_priority(graph, node)
               if priority > current_priority:
                    heapq.heappush(priority_queue, (current_priority, node))
                    continue
               
               self._contract_node(graph, node)
               self.node_order.append(node)
               processed_nodes.add(node)
          
          self.node_levels = {node: i for i, node in enumerate(self.node_order)}
          self.shortcut_graph = graph
          
          end_time = time.time()
          self.preprocessing_time = (end_time - start_time) * 1000 # in ms
          
          space_graph = 0
          
          space_graph += self.dataUtils.get_deep_size(list(self.shortcut_graph.nodes))
          space_graph += self.dataUtils.get_deep_size(list(self.shortcut_graph.edges(data=True)))
          
          space_levels = self.dataUtils.get_deep_size(self.node_levels)
          space_order = self.dataUtils.get_deep_size(self.node_order)
          
          self.space_preprocessing_bytes = space_graph + space_levels + space_order

    def _calculate_priority(self, graph, node):

        neighbors = list(graph.neighbors(node))
        shortcuts_to_add = 0
        
        # Edge Difference calculation
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                u, v = neighbors[i], neighbors[j]
                if not graph.has_edge(u, v):
                    shortcuts_to_add += 1
        
        edge_difference = shortcuts_to_add - graph.degree(node)
        
        priority = edge_difference * 10 + graph.degree(node)
        return priority

    def _contract_node(self, graph, node):
         
        neighbors = list(graph.neighbors(node))
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                u, v = neighbors[i], neighbors[j]
                
                weight_un = graph[u][node].get('weight', 1)
                weight_nv = graph[node][v].get('weight', 1)
                shortcut_weight = weight_un + weight_nv

                # if an edge already exists, is it shorter?
                if graph.has_edge(u, v):
                    if graph[u][v].get('weight', 1) > shortcut_weight:
                         graph.add_edge(u, v, weight=shortcut_weight)
                else:
                    # If no edge exists, we must add the shortcut
                    graph.add_edge(u, v, weight=shortcut_weight)
        
        # In a real implementation, we would remove `node` and its edges.
        # For simplicity with NetworkX, we can just leave it, as the query
        # algorithm will naturally "skip over" it due to the level check.

    def query(self, start_node, end_node):
          # bidirectional dijkstra
          start_time = time.time()

          forward_dist = {node: float('inf') for node in self.original_graph.nodes}
          backward_dist = {node: float('inf') for node in self.original_graph.nodes}
          
          forward_dist[start_node] = 0
          backward_dist[end_node] = 0
          
          forward_queue = [(0, start_node)]
          backward_queue = [(0, end_node)]
          
          min_dist = float('inf')
          meeting_node = None
          explored_nodes = 0

          while forward_queue and backward_queue:
               
               if forward_queue[0][0] + backward_queue[0][0] >= min_dist:
                    break

               dist_f, u = heapq.heappop(forward_queue)
               explored_nodes += 1
               
               if dist_f > min_dist: continue

               if backward_dist[u] != float('inf'):
                    if dist_f + backward_dist[u] < min_dist:
                         min_dist = dist_f + backward_dist[u]
                         meeting_node = u

               for v in self.shortcut_graph.neighbors(u):
                    if self.node_levels[v] > self.node_levels[u]:
                         weight = self.shortcut_graph[u][v].get('weight', 1)
                         if forward_dist[u] + weight < forward_dist[v]:
                              forward_dist[v] = forward_dist[u] + weight
                              heapq.heappush(forward_queue, (forward_dist[v], v))

               dist_b, u = heapq.heappop(backward_queue)
               explored_nodes += 1

               if dist_b > min_dist: continue

               if forward_dist[u] != float('inf'):
                    if dist_b + forward_dist[u] < min_dist:
                         min_dist = dist_b + forward_dist[u]
                         meeting_node = u
               
               for v in self.shortcut_graph.neighbors(u):
                    if self.node_levels[v] > self.node_levels[u]:
                         weight = self.shortcut_graph[u][v].get('weight', 1)
                         if backward_dist[u] + weight < backward_dist[v]:
                              backward_dist[v] = backward_dist[u] + weight
                              heapq.heappush(backward_queue, (backward_dist[v], v))

          end_time = time.time()
          elapsed_time = (end_time - start_time) * 1000

          query_space = (self.dataUtils.get_deep_size(forward_dist) +
                         self.dataUtils.get_deep_size(backward_dist) +
                         self.dataUtils.get_deep_size(forward_queue) +
                         self.dataUtils.get_deep_size(backward_queue))  
          
          return {
               'start_node': start_node,
               'end_node': end_node,
               'preprocessing_time (ms)': self.preprocessing_time,
               'execution_time (ms)': elapsed_time,
               'explored_nodes': explored_nodes,
               'space_occupation (Byte)': query_space + self.space_preprocessing_bytes,
               'space_preprocessing (Byte)': self.space_preprocessing_bytes,
               'space_query (Byte)': query_space,
          }

    def run(self, graph, num_queries, start_node_list, end_node_list):
         
        self.original_graph = graph.graph
        print("Starting CH preprocessing...")
        self.preprocess()
        print(f"Preprocessing finished in {self.preprocessing_time:.2f} ms.")
        
        results = []
        for i in range(num_queries):
            start_node = start_node_list[i]
            end_node = end_node_list[i]
            result = self.query(start_node, end_node)
            results.append(result)
        
        self.dataUtils.save_to_csv('contraction_hieraarchies_results.csv', results)
        print(f"Saved contraction hierarchies results")