
import heapq
import time
import sys


from utils.utils import RawData

class Dijkstra:
     def __init__(self):
          self.graph = None
          self.num_queries = 0
          self.results = []
          self.dataUtils = RawData()
          
     def run(self, graph, num_queries, start_node_list, end_node_list):
          self.graph = graph
          self.num_queries = num_queries
          
          # randomize start and end nodes for each query
          for i in range(num_queries):
               start_node = start_node_list[i]
               end_node = end_node_list[i]
               result = self._real_dijkstra(start_node, end_node)
               self.results.append(result)

          #save self.results to CSV
          self._save_results_to_csv()

     def _real_dijkstra(self, start_node, end_node):
          # start the timer
          start_time = time.time()

          graph_nx = self.graph.graph
          distances = {node: float('inf') for node in graph_nx.nodes}
          previous = {node: None for node in graph_nx.nodes}
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

               for neighbor in graph_nx.neighbors(current_node):
                    weight = graph_nx[current_node][neighbor].get('weight', 1)
                    distance = current_dist + weight
                    if distance < distances[neighbor]:
                         distances[neighbor] = distance
                         previous[neighbor] = current_node
                         heapq.heappush(queue, (distance, neighbor))

          # Ricostruisci il percorso
          path = []
          node = end_node
          if distances[end_node] != float('inf'):
               while node is not None:
                    path.insert(0, node)
                    node = previous[node]
          else:
               path = None  # Nessun percorso trovato

          end_time = time.time()
          elapsed_time = (end_time - start_time)* 1000  # Converti in millisecondi

          return {
               'start_node': start_node,
               'end_node': end_node,
               'preproccessing_time': 0,  # Non implementato
               'execution_time (ms)': elapsed_time,
               'explored_nodes': len(visited),
               # 'space_occupation:': len(distances) + len(previous) + len(queue)
               'space_occupation (Byte):': sys.getsizeof(distances) + sys.getsizeof(previous) + sys.getsizeof(queue)
          }
     
     def _save_results_to_csv(self):
          self.dataUtils.save_to_csv('dijkstra_results.csv', self.results) 