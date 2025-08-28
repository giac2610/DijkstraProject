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

    def preprocess(self):
        start_time = time.time()
        graph = self.original_graph.copy()

        priority_queue = [
            (self._calculate_priority(graph, node), node) for node in range(graph.vcount())
        ]
        heapq.heapify(priority_queue)
        
        self.node_order = []
        processed_nodes = set()

        while priority_queue:
            priority, node = heapq.heappop(priority_queue)

            if node in processed_nodes:
                continue

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
        self.preprocessing_time = (end_time - start_time) * 1000

        space_graph = self.dataUtils.get_deep_size(self.shortcut_graph.get_edgelist())
        space_levels = self.dataUtils.get_deep_size(self.node_levels)
        space_order = self.dataUtils.get_deep_size(self.node_order)
        self.space_preprocessing_bytes = space_graph + space_levels + space_order

    def _calculate_priority(self, graph, node):
        if graph.degree(node) == 0:
            return float('inf')

        neighbors = graph.neighbors(node)
        shortcuts_to_add = 0
        
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                u, v = neighbors[i], neighbors[j]
                if graph.get_eid(u, v, error=False) == -1:
                    shortcuts_to_add += 1
        
        edge_difference = shortcuts_to_add - graph.degree(node)
        priority = edge_difference * 10 + graph.degree(node)
        return priority

    def _contract_node(self, graph, node):
        neighbors = graph.neighbors(node)
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                u, v = neighbors[i], neighbors[j]
                weight_un = graph.es[graph.get_eid(u, node)]['weight']
                weight_nv = graph.es[graph.get_eid(node, v)]['weight']
                shortcut_weight = weight_un + weight_nv

                eid = graph.get_eid(u, v, error=False)
                if eid != -1:
                    if graph.es[eid]['weight'] > shortcut_weight:
                        graph.es[eid]['weight'] = shortcut_weight
                else:
                    graph.add_edge(u, v, weight=shortcut_weight)

        incident_edges = graph.incident(node, mode='all')
        if incident_edges:
            graph.delete_edges(incident_edges)

    def query(self, start_node, end_node):
        start_time = time.time()
        forward_dist = {node: float('inf') for node in range(self.original_graph.vcount())}
        backward_dist = {node: float('inf') for node in range(self.original_graph.vcount())}
        forward_dist[start_node] = 0
        backward_dist[end_node] = 0
        forward_queue = [(0, start_node)]
        backward_queue = [(0, end_node)]
        min_dist = float('inf')
        
        # --- Misurazione Realistica dei Nodi Esplorati ---
        explored_nodes = 0

        while forward_queue and backward_queue:
            if forward_queue[0][0] + backward_queue[0][0] >= min_dist:
                break

            # Esplorazione dalla ricerca in avanti
            dist_f, u = heapq.heappop(forward_queue)
            explored_nodes += 1
            if dist_f > min_dist: continue

            if backward_dist[u] != float('inf'):
                min_dist = min(min_dist, dist_f + backward_dist[u])

            for v_id in self.shortcut_graph.neighbors(u):
                if self.node_levels.get(v_id, -1) > self.node_levels.get(u, -1):
                    eid = self.shortcut_graph.get_eid(u, v_id)
                    weight = self.shortcut_graph.es[eid]['weight']
                    if forward_dist[u] + weight < forward_dist[v_id]:
                        forward_dist[v_id] = forward_dist[u] + weight
                        heapq.heappush(forward_queue, (forward_dist[v_id], v_id))

            if not backward_queue: break

            # Esplorazione dalla ricerca all'indietro
            dist_b, u = heapq.heappop(backward_queue)
            explored_nodes += 1
            if dist_b > min_dist: continue

            if forward_dist[u] != float('inf'):
                min_dist = min(min_dist, dist_b + forward_dist[u])
            
            for v_id in self.shortcut_graph.neighbors(u):
                if self.node_levels.get(v_id, -1) > self.node_levels.get(u, -1):
                    eid = self.shortcut_graph.get_eid(u, v_id)
                    weight = self.shortcut_graph.es[eid]['weight']
                    if backward_dist[u] + weight < backward_dist[v_id]:
                        backward_dist[v_id] = backward_dist[u] + weight
                        heapq.heappush(backward_queue, (backward_dist[v_id], v_id))

        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        
        # --- Misurazione Realistica dello Spazio di Query ---
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