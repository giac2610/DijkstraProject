import time
import sys
import heapq
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

    def _witness_search(self, graph, start_node, target_node, max_dist_to_beat):
        """
        Esegue una Dijkstra che si ferma non appena la distanza attuale
        supera la 'distanza da battere' (max_dist_to_beat). 
        """
        distances = {start_node: 0}
        pq = [(0, start_node)]
        
        while pq:
            dist, u = heapq.heappop(pq)
            
            # se siamo già oltre la dist to beat è inutile continuare a esplorare questo ramo.
            if dist > max_dist_to_beat:
                continue

            if u == target_node:
                return dist
                
            if dist > distances.get(u, float('inf')):
                continue

            for v in graph.neighbors(u, mode='out'):
                weight = graph.es[graph.get_eid(u, v)]['weight']
                new_dist = dist + weight
                
                # non aggiungiamo alla coda percorsi già perdenti
                if new_dist < distances.get(v, float('inf')) and new_dist <= max_dist_to_beat:
                    distances[v] = new_dist
                    heapq.heappush(pq, (new_dist, v))
        return distances.get(target_node, float('inf'))

    def _contract_node(self, current_graph, node):
        predecessors = list(current_graph.neighbors(node, mode='in'))
        successors = list(current_graph.neighbors(node, mode='out'))
        
        for u in predecessors:
            for v in successors:
                if u == v: continue
                shortcut_weight = current_graph.es[current_graph.get_eid(u, node)]['weight'] + current_graph.es[current_graph.get_eid(node, v)]['weight']
                
            
                witness_dist = self._witness_search(current_graph, u, v, shortcut_weight)
                
                if shortcut_weight < witness_dist:
                    eid = current_graph.get_eid(u, v, error=False)
                    if eid != -1:
                        if current_graph.es[eid]['weight'] > shortcut_weight:
                            current_graph.es[eid]['weight'] = shortcut_weight
                    else:
                        current_graph.add_edge(u, v, weight=shortcut_weight)

    def preprocess(self):
        start_time = time.time()
        
        node_priorities = []
        # Calcoliamo le priorità sul grafo originale
        for node in range(self.original_graph.vcount()):
            predecessors = self.original_graph.neighbors(node, mode='in')
            successors = self.original_graph.neighbors(node, mode='out')
            shortcuts_to_add = 0
            for u in predecessors:
                for v in successors:
                    if u != v and self.original_graph.get_eid(u, v, error=False) == -1:
                        shortcuts_to_add += 1
            edge_difference = shortcuts_to_add - (len(predecessors) + len(successors))
            priority = (edge_difference, len(predecessors) + len(successors))
            node_priorities.append((priority, node))
            
        node_priorities.sort(key=lambda x: x[0])
        self.node_order = [node for priority, node in node_priorities]
        self.node_levels = {node: i for i, node in enumerate(self.node_order)}
        
        self.shortcut_graph = self.original_graph.copy()
        for i, node in enumerate(self.node_order):
            self._contract_node(self.shortcut_graph, node)
            
        end_time = time.time()
        self.preprocessing_time = (end_time - start_time) * 1000
        self.space_preprocessing_bytes = (self.dataUtils.get_deep_size(self.shortcut_graph.get_edgelist()) + 
                                          self.dataUtils.get_deep_size(self.node_levels) + 
                                          self.dataUtils.get_deep_size(self.node_order))

    def query(self, start_node, end_node):
        start_time = time.time()
        forward_dist = {node: float('inf') for node in range(self.original_graph.vcount())}
        backward_dist = {node: float('inf') for node in range(self.original_graph.vcount())}
        forward_dist[start_node] = 0
        backward_dist[end_node] = 0
        forward_queue = [(0, start_node)]
        backward_queue = [(0, end_node)]
        min_dist = float('inf')
        explored_nodes = 0

        while forward_queue or backward_queue:
            if forward_queue and backward_queue:
                if forward_queue[0][0] + backward_queue[0][0] >= min_dist: break
            
            if forward_queue and (not backward_queue or forward_queue[0][0] <= backward_queue[0][0]):
                dist_f, u = heapq.heappop(forward_queue)
                explored_nodes += 1
                if backward_dist.get(u, float('inf')) != float('inf'):
                    min_dist = min(min_dist, dist_f + backward_dist[u])
                for v_id in self.shortcut_graph.neighbors(u, mode="out"):
                    if self.node_levels.get(v_id, -1) > self.node_levels.get(u, -1):
                        eid = self.shortcut_graph.get_eid(u, v_id)
                        weight = self.shortcut_graph.es[eid]['weight']
                        if forward_dist.get(u, float('inf')) + weight < forward_dist.get(v_id, float('inf')):
                            forward_dist[v_id] = forward_dist[u] + weight
                            heapq.heappush(forward_queue, (forward_dist[v_id], v_id))
            elif backward_queue:
                dist_b, u = heapq.heappop(backward_queue)
                explored_nodes += 1
                if forward_dist.get(u, float('inf')) != float('inf'):
                    min_dist = min(min_dist, dist_b + forward_dist[u])
                for v_id in self.shortcut_graph.neighbors(u, mode="in"):
                    if self.node_levels.get(v_id, -1) > self.node_levels.get(u, -1):
                        eid = self.shortcut_graph.get_eid(v_id, u)
                        weight = self.shortcut_graph.es[eid]['weight']
                        if backward_dist.get(u, float('inf')) + weight < backward_dist.get(v_id, float('inf')):
                            backward_dist[v_id] = backward_dist[u] + weight
                            heapq.heappush(backward_queue, (backward_dist[v_id], v_id))
            else:
                break

        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        query_space = (self.dataUtils.get_deep_size(forward_dist) + self.dataUtils.get_deep_size(backward_dist))
        return {
            'tot nodes': self.original_graph.vcount(), 
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
        print("appending results...")
        for i in range(num_queries):
            start_node = start_node_list[i]
            end_node = end_node_list[i]
            result = self.query(start_node, end_node)
            results.append(result)
        
        return results
        # self.dataUtils.save_to_csv('contraction_hierarchies_results.csv', results)
        # print(f"Saved contraction hierarchies results")
