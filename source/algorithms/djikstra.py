
import heapq
import time
import sys
from utils.utils import RawData

class Dijkstra:
     def __init__(self):
          self.graph = None
          self.num_queries = 0
          # self.results = []
          self.dataUtils = RawData()
          
     def run(self, graph, num_queries, start_node_list, end_node_list):
          self.graph = graph.graph
          results = []
          # get randomized start and end nodes for each query
          for i in range(num_queries):
               start_node = start_node_list[i]
               end_node = end_node_list[i]
               result = self._real_dijkstra(start_node, end_node)
               results.append(result)

          return results
          # self._save_results_to_csv()

     def _real_dijkstra(self, start_node, end_node):
          # start the timer
          start_time = time.time()
          graph_ig = self.graph
          distances = {node: float('inf') for node in range(graph_ig.vcount())}
          previous = {node: None for node in range(graph_ig.vcount())}
          distances[start_node] = 0

          queue = [(0, start_node)]
          visited = set()

          while queue:
               current_dist, current_node = heapq.heappop(queue)
               if current_node in visited:
                    continue
               visited.add(current_node)

               if current_node == end_node:
                    break

               for neighbor in graph_ig.neighbors(current_node, mode="out"):
                    eid = graph_ig.get_eid(current_node, neighbor)
                    weight = graph_ig.es[eid]['weight']
                    distance = current_dist + weight
                    if distance < distances[neighbor]:
                         distances[neighbor] = distance
                         previous[neighbor] = current_node
                         heapq.heappush(queue, (distance, neighbor))
          end_time = time.time()
          elapsed_time = (end_time - start_time)* 1000  # Converti in millisecondi

          # Ricostruisci il percorso
          path = []
          curr = end_node
          if distances.get(curr, float('inf')) != float('inf'):
               while curr is not None:
                    path.append(curr)
                    curr = previous.get(curr)
               path.reverse()
          
          final_path_weight = distances.get(end_node, float('inf'))
          if final_path_weight == float('inf'): final_path_weight = -1

          space_ocupation = self.dataUtils.get_deep_size(distances) + self.dataUtils.get_deep_size(previous) + self.dataUtils.get_deep_size(queue)
          
          return {
               'tot nodes': graph_ig.vcount(),
               'start_node': start_node,
               'end_node': end_node,
               'preproccessing_time (ms)': 0,  
               'execution_time (ms)': elapsed_time,
               'explored_nodes': len(visited),
               'space_occupation (Byte):': space_ocupation,
               'path': path if path else 'No path found',
               'path_weight': final_path_weight,
          }