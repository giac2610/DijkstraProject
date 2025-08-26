import time
import sys
import heapq

from utils.utils import RawData

class Contraction_Hierarchies:
     def __init__(self):
          self.graph = None
          self.num_queries = 0
          self.results_degree = []
          self.results_edge_diff = []
          self.dataUtils = RawData()
          self.shortcut_graph = None  # Grafo con shortcut
     
     def run(self, graph, num_queries, start_node_list, end_node_list):
          self.graph = graph
          
          # Calcola tempo di preprocessing per node degree priority
          start_pre = time.time()
          node_order = self._node_degree_priority()
          end_pre = time.time()
          preprocessing_time_degree = (end_pre - start_pre) * 1000  # ms
          self._add_shortcuts(node_order)
          # randomize start and end nodes for each query for degree priority
          for i in range(num_queries):
               start_node = start_node_list[i]
               end_node = end_node_list[i]
               result = self._ch_algorithm(start_node, end_node, node_order, preprocessing_time_degree)
               self.results_degree.append(result)
          
          self._save_results_to_csv("contraction_hierarchies_node_degree.csv", self.results_degree)

          # Calcola tempo di preprocessing per edge difference priority
          start_pre = time.time()
          edge_order = self._edge_difference_priority()
          end_pre = time.time()
          preprocessing_time_edge = (end_pre - start_pre) * 1000  # ms
          
          # randomize start and end nodes for each query for edge difference priority
          for i in range(num_queries):
               start_node = start_node_list[i]
               end_node = end_node_list[i]
               result = self._ch_algorithm(start_node, end_node, edge_order,  preprocessing_time_edge)
               self.results_edge_diff.append(result)
          self._save_results_to_csv("contraction_hierarchies_edge_difference.csv", self.results_edge_diff)
          

     def _node_degree_priority(self):
          sorted_nodes = sorted(self.graph.graph.nodes, key=lambda n: self.graph.graph.degree(n))
          return  sorted_nodes
     
     def _edge_difference_priority(self):
          nx_graph = self.graph.graph
          priorities = {}
          for node in nx_graph.nodes:
               neighbors = list(nx_graph.neighbors(node))
               original_edges = len(neighbors)
               shortcut_edges = 0
               for i in range(len(neighbors)):
                    for j in range(i+1, len(neighbors)):
                         u, v = neighbors[i], neighbors[j]
                    if not nx_graph.has_edge(u, v):
                         shortcut_edges += 1
               priorities[node] = shortcut_edges - original_edges
          sorted_nodes = sorted(priorities, key=lambda n: priorities[n])
          return sorted_nodes
          
     def _add_shortcuts(self, node_order):
          nx_graph = self.graph.graph.copy()
          for node in node_order:
               neighbors = list(nx_graph.neighbors(node))
               for i in range(len(neighbors)):
                    for j in range(i+1, len(neighbors)):
                         u, v = neighbors[i], neighbors[j]
                         if not nx_graph.has_edge(u, v):
                              shortcut_weight = nx_graph[node][u].get('weight', 1) + nx_graph[node][v].get('weight', 1)

                              alt_path = self._local_shortest_path(nx_graph, u, v, shortcut_weight, node)

                              if alt_path > shortcut_weight:
                                   nx_graph.add_edge(u, v, weight=shortcut_weight)
          self.shortcut_graph = nx_graph


     def _local_shortest_path(self, graph, source, target, max_dist, forbidden):
          dist = {node: float('inf') for node in graph.nodes}
          dist[source] = 0
          queue = [(0, source)]

          while queue:
               d, node = heapq.heappop(queue)
               if d > max_dist:
                    return float('inf')
               if node == target:
                    return d
               for neighbor in graph.neighbors(node):
                    if neighbor == forbidden:
                         continue
                    w = graph[node][neighbor].get('weight', 1)
                    nd = d + w
                    if nd < dist[neighbor]:
                         dist[neighbor] = nd
                         heapq.heappush(queue, (nd, neighbor))
          return float('inf')


     def _ch_algorithm(self, start_node, end_node, node_order, preprocessing_time):
          import heapq
          start_time = time.time()

          level = {node: i for i, node in enumerate(node_order)}
          graph = self.shortcut_graph

          forward_dist = {node: float('inf') for node in graph.nodes}
          backward_dist = {node: float('inf') for node in graph.nodes}
          forward_dist[start_node] = 0
          backward_dist[end_node] = 0
          forward_queue = [(0, start_node)]
          backward_queue = [(0, end_node)]
          forward_visited = set()
          backward_visited = set()
          explored_nodes = 0
          min_dist = float('inf')

          while forward_queue or backward_queue:
               if forward_queue:
                    dist, node = heapq.heappop(forward_queue)
                    if node not in forward_visited:
                         forward_visited.add(node)
                         explored_nodes += 1
                         for neighbor in graph.neighbors(node):
                              if level[neighbor] > level[node]:
                                   weight = graph[node][neighbor].get('weight', 1)
                                   new_dist = dist + weight
                                   if new_dist < forward_dist[neighbor]:
                                        forward_dist[neighbor] = new_dist
                                        heapq.heappush(forward_queue, (new_dist, neighbor))
               if backward_queue:
                    dist, node = heapq.heappop(backward_queue)
                    if node not in backward_visited:
                         backward_visited.add(node)
                         explored_nodes += 1
                         for neighbor in graph.neighbors(node):
                              if level[neighbor] < level[node]:
                                   weight = graph[node][neighbor].get('weight', 1)
                                   new_dist = dist + weight
                                   if new_dist < backward_dist[neighbor]:
                                        backward_dist[neighbor] = new_dist
                                        heapq.heappush(backward_queue, (new_dist, neighbor))
               # Controlla meeting point
               meeting_nodes = forward_visited & backward_visited
               for n in meeting_nodes:
                    total = forward_dist[n] + backward_dist[n]
                    if total < min_dist:
                         min_dist = total

          end_time = time.time()
          elapsed_time = (end_time - start_time) * 1000  # ms

          return {
               'start_node': start_node,
               'end_node': end_node,
               'preproccessing_time': preprocessing_time,
               'execution_time (ms)': elapsed_time,
               'explored_nodes': explored_nodes,
               'space_occupation (Byte):': sys.getsizeof(forward_dist) + sys.getsizeof(backward_dist) + sys.getsizeof(forward_queue) + sys.getsizeof(backward_queue) + sys.getsizeof(node_order)
          }

     def _save_results_to_csv(self, name, results):
          self.dataUtils.save_to_csv(name, results)