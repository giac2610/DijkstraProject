import time
import heapq
import numpy as np
from utils.utils import RawData
import sys

class Contraction_Hierarchies:
    def __init__(self, graph=None):
        self.original_graph = graph.graph if graph else None
        self.dataUtils = RawData()
        self.shortcut_graph = None
        self.node_order = None
        self.node_levels = None
        self.preprocessing_time = 0.0
        self.space_preprocessing_bytes = 0
        
        # Per la Witness Search
        self.adj = None
        self.dist_ws = None
        self.visited_ws = None
        # Per la Query
        self.dist_fwd = None
        self.dist_bwd = None
        self.prev_fwd = None
        self.prev_bwd = None

    def _build_adjacency(self):
        print("Pre-calcolo della lista di adiacenza per ottimizzazione...")
        n = self.original_graph.vcount()
        adj = [[] for _ in range(n)]
        for e in self.original_graph.es:
            u, v = e.tuple
            w = e["weight"]
            adj[u].append((v, w))
        return adj

    def _init_scratchpads(self):
        print("Inizializzazione degli array scratchpad (numpy)...")
        n = self.original_graph.vcount()
        # Per Witness Search
        self.dist_ws = np.full(n, np.inf, dtype=float)
        self.visited_ws = np.zeros(n, dtype=bool)
        # Per Query
        self.dist_fwd = np.full(n, np.inf, dtype=float)
        self.dist_bwd = np.full(n, np.inf, dtype=float)
        self.prev_fwd = np.full(n, -1, dtype=int)
        self.prev_bwd = np.full(n, -1, dtype=int)

    def _witness_search(self, start_node, target_node, max_dist_to_beat, hop_limit=6):
        pq = [(0.0, start_node)]
        touched_nodes = [start_node]
        self.dist_ws[start_node] = 0.0
        self.visited_ws[start_node] = True
        
        final_dist = np.inf
        while pq:
            dist_u, u = heapq.heappop(pq)
            if dist_u > max_dist_to_beat: break
            if u == target_node:
                final_dist = dist_u
                break
            if dist_u > self.dist_ws[u]: continue
            if len(touched_nodes) > hop_limit: continue
            
            for v, weight_uv in self.adj[u]:
                new_dist = dist_u + weight_uv
                if new_dist < self.dist_ws[v]:
                    self.dist_ws[v] = new_dist
                    heapq.heappush(pq, (new_dist, v))
                    if not self.visited_ws[v]:
                        touched_nodes.append(v)
                        self.visited_ws[v] = True
        
        for node in touched_nodes:
            self.dist_ws[node] = np.inf
            self.visited_ws[node] = False
        return final_dist

    def _contract_node(self, current_graph, node):
        predecessors = list(current_graph.neighbors(node, mode='in'))
        successors = list(current_graph.neighbors(node, mode='out'))
        for u in predecessors:
            for v in successors:
                if u == v: continue
                shortcut_weight = (
                    current_graph.es[current_graph.get_eid(u, node)]['weight'] +
                    current_graph.es[current_graph.get_eid(node, v)]['weight']
                )
                eid_existing = current_graph.get_eid(u, v, error=False)
                if eid_existing != -1 and current_graph.es[eid_existing]['weight'] <= shortcut_weight:
                    continue
                witness_dist = self._witness_search(u, v, shortcut_weight)
                if shortcut_weight <= witness_dist:
                    if eid_existing != -1:
                        edge = current_graph.es[eid_existing]
                        if edge['weight'] > shortcut_weight:
                            edge['weight'] = shortcut_weight
                            edge['middle_node'] = node
                    else:
                        current_graph.add_edge(u, v, weight=shortcut_weight, middle_node=node)

    def preprocess(self):
        start_time = time.time()
        print("Calcolo delle priorità iniziali (metodo statico)...")
        node_priorities = []
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
            
        print("Ordinamento dei nodi...")
        node_priorities.sort(key=lambda x: x[0])
        self.node_order = [node for priority, node in node_priorities]
        self.node_levels = {node: i for i, node in enumerate(self.node_order)}
        
        self.shortcut_graph = self.original_graph.copy()
        self.shortcut_graph.es['middle_node'] = [None] * self.shortcut_graph.ecount()

        self.adj = self._build_adjacency()
        self._init_scratchpads()
        
        print("Avvio della contrazione sequenziale...")
        for i, node in enumerate(self.node_order):
            if i % 1000 == 0:
                 print(f"  Contrazione nodo {i}/{len(self.node_order)}...")
            self._contract_node(self.shortcut_graph, node)
            
        end_time = time.time()
        self.preprocessing_time = (end_time - start_time) * 1000
        
        self.space_preprocessing_bytes = (
            self.shortcut_graph.ecount() * (sys.getsizeof(int()) * 2 + sys.getsizeof(float())) + 
            len(self.node_levels) * (sys.getsizeof(int()) * 2)
        )

    def _unpack_path(self, u, v):
        edge_id = self.shortcut_graph.get_eid(u, v, error=False)
        if edge_id == -1: return [u] 
        edge = self.shortcut_graph.es[edge_id]
        if edge['middle_node'] is None:
            return [u, v]
        middle_node = int(edge['middle_node'])
        path1 = self._unpack_path(u, middle_node)
        path2 = self._unpack_path(middle_node, v)
        return path1[:-1] + path2

    def query(self, start_node, end_node):
        start_time = time.time()
        
        self.dist_fwd[start_node] = 0.0
        self.dist_bwd[end_node] = 0.0
        
        touched_nodes_fwd = {start_node}
        touched_nodes_bwd = {end_node}

        forward_queue = [(0.0, start_node)]
        backward_queue = [(0.0, end_node)]
        min_dist = np.inf
        meeting_node = -1
        explored_nodes = 0

        while forward_queue or backward_queue:
            if forward_queue and backward_queue:
                if forward_queue[0][0] + backward_queue[0][0] >= min_dist: break
            
            if forward_queue and (not backward_queue or forward_queue[0][0] <= backward_queue[0][0]):
                dist_f, u = heapq.heappop(forward_queue)
                explored_nodes += 1
                if self.dist_bwd[u] != np.inf:
                    current_dist = dist_f + self.dist_bwd[u]
                    if current_dist < min_dist:
                        min_dist = current_dist
                        meeting_node = u
                for v_id in self.shortcut_graph.neighbors(u, mode="out"):
                    if self.node_levels.get(v_id, -1) > self.node_levels.get(u, -1):
                        eid = self.shortcut_graph.get_eid(u, v_id)
                        weight = self.shortcut_graph.es[eid]['weight']
                        if self.dist_fwd[u] + weight < self.dist_fwd[v_id]:
                            self.dist_fwd[v_id] = self.dist_fwd[u] + weight
                            self.prev_fwd[v_id] = u
                            heapq.heappush(forward_queue, (self.dist_fwd[v_id], v_id))
                            touched_nodes_fwd.add(v_id)
            elif backward_queue:
                dist_b, u = heapq.heappop(backward_queue)
                explored_nodes += 1
                if self.dist_fwd[u] != np.inf:
                    current_dist = dist_b + self.dist_fwd[u]
                    if current_dist < min_dist:
                        min_dist = current_dist
                        meeting_node = u
                for v_id in self.shortcut_graph.neighbors(u, mode="in"):
                    if self.node_levels.get(v_id, -1) > self.node_levels.get(u, -1):
                        eid = self.shortcut_graph.get_eid(v_id, u)
                        weight = self.shortcut_graph.es[eid]['weight']
                        if self.dist_bwd[u] + weight < self.dist_bwd[v_id]:
                            self.dist_bwd[v_id] = self.dist_bwd[u] + weight
                            self.prev_bwd[v_id] = u
                            heapq.heappush(backward_queue, (self.dist_bwd[v_id], v_id))
                            touched_nodes_bwd.add(v_id)
            else:
                break
        
        path = []
        if meeting_node != -1:
            shortcut_path_forward = []
            curr = meeting_node
            while curr != -1:
                shortcut_path_forward.append(curr)
                curr = self.prev_fwd[curr]
            shortcut_path_forward.reverse()
            shortcut_path_backward = []
            curr = self.prev_bwd[meeting_node]
            while curr != -1:
                shortcut_path_backward.append(curr)
                curr = self.prev_bwd[curr]
            shortcut_path = shortcut_path_forward + shortcut_path_backward
            if shortcut_path:
                path = [shortcut_path[0]]
                for i in range(len(shortcut_path) - 1):
                    u, v = shortcut_path[i], shortcut_path[i+1]
                    unpacked_segment = self._unpack_path(u, v)
                    path.extend(unpacked_segment[1:])

        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        
        # Pulizia efficiente degli scratchpad della query
        for node in touched_nodes_fwd:
            self.dist_fwd[node] = np.inf
            self.prev_fwd[node] = -1
        for node in touched_nodes_bwd:
            self.dist_bwd[node] = np.inf
            self.prev_bwd[node] = -1

        query_space = self.dist_fwd.nbytes + self.dist_bwd.nbytes + self.prev_fwd.nbytes + self.prev_bwd.nbytes
        
        return {
            'graph_name': 'N/A',
            'tot nodes': self.original_graph.vcount(),
            'start_node': start_node,
            'end_node': end_node,
            'preprocessing_time (ms)': self.preprocessing_time,
            'execution_time (ms)': elapsed_time if min_dist != np.inf else -1,
            'explored_nodes': explored_nodes,
            'path_weight': min_dist if min_dist != np.inf else -1,
            'path': path if path else 'No path found',
            'space_occupation (Byte)': query_space + self.space_preprocessing_bytes
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
        return results

