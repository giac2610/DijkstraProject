import time
import sys
import heapq
from utils.utils import RawData

class Contraction_Hierarchies:
    def __init__(self, graph=None):
        self.original_graph = graph.graph if graph else None
        self.dataUtils = RawData()
        self.shortcut_graph = None
        self.node_order = None
        self.node_levels = None
        self.preprocessing_time = 0.0
        self.space_preprocessing_bytes = 0

    def _witness_search(self, graph, start_node, target_node, max_dist_to_beat, hop_limit=15):
        distances = {start_node: 0}
        pq = [(0, start_node)]
        hops = 0
        while pq and hops < hop_limit:
            hops += 1
            dist, u = heapq.heappop(pq)
            if dist > max_dist_to_beat: continue
            if u == target_node: return dist
            if dist > distances.get(u, float('inf')): continue
            for v in graph.neighbors(u, mode='out'):
                weight = graph.es[graph.get_eid(u, v)]['weight']
                new_dist = dist + weight
                if new_dist < distances.get(v, float('inf')) and new_dist <= max_dist_to_beat:
                    distances[v] = new_dist
                    heapq.heappush(pq, (new_dist, v))
        return distances.get(target_node, float('inf'))

    def _calculate_priority(self, graph, node):
        predecessors = graph.neighbors(node, mode='in')
        successors = graph.neighbors(node, mode='out')
        shortcuts_to_add = 0
        for u in predecessors:
            for v in successors:
                if u != v and graph.get_eid(u, v, error=False) == -1:
                    shortcuts_to_add += 1
        edge_difference = shortcuts_to_add - (len(predecessors) + len(successors))
        # Aggiungiamo altri fattori per una priorità più robusta
        priority = edge_difference * 10 + len(predecessors) + len(successors)
        return priority

    def _contract_node(self, current_graph, node):
        predecessors = list(current_graph.neighbors(node, mode='in'))
        successors = list(current_graph.neighbors(node, mode='out'))
        for u in predecessors:
            for v in successors:
                if u == v: continue
                shortcut_weight = current_graph.es[current_graph.get_eid(u, node)]['weight'] + current_graph.es[current_graph.get_eid(node, v)]['weight']
                witness_dist = self._witness_search(self.original_graph, u, v, shortcut_weight)
                if shortcut_weight <= witness_dist:
                    eid = current_graph.get_eid(u, v, error=False)
                    if eid != -1:
                        edge = current_graph.es[eid]
                        if edge['weight'] > shortcut_weight:
                            edge['weight'] = shortcut_weight
                            edge['middle_node'] = node
                    else:
                        current_graph.add_edge(u, v, weight=shortcut_weight, middle_node=node)

    def preprocess(self):
        """
        --- PRE-PROCESSING DINAMICO CON LAZY UPDATING ---
        Implementa la logica di aggiornamento della priorità per un ordine di 
        contrazione più efficiente e un pre-processing più veloce.
        """
        start_time = time.time()
        
        # Lavoriamo su una copia del grafo che possiamo modificare
        contraction_graph = self.original_graph.copy()
        
        # 1. Calcolo delle priorità iniziali
        print("Calcolo delle priorità iniziali...")
        priorities = {node: self._calculate_priority(contraction_graph, node) for node in range(contraction_graph.vcount())}
        priority_queue = [(p, n) for n, p in priorities.items()]
        heapq.heapify(priority_queue)
        
        self.node_order = []
        processed_nodes = set()
        
        total_nodes = contraction_graph.vcount()
        count = 0
        while len(processed_nodes) < total_nodes:
            if not priority_queue: break

            p, node = heapq.heappop(priority_queue)

            # Se il nodo è già stato processato, saltalo
            if node in processed_nodes:
                continue
            
            # --- LAZY UPDATE CHECK ---
            # Ricalcola la priorità e verifica se quella estratta dalla coda è obsoleta.
            current_priority = self._calculate_priority(contraction_graph, node)
            if p > current_priority:
                # La priorità è cambiata e peggiorata; rimettiamo il nodo in coda con il valore corretto.
                priorities[node] = current_priority
                heapq.heappush(priority_queue, (current_priority, node))
                continue
            
            # Se la priorità è ancora la migliore, procediamo con la contrazione
            self._contract_node(contraction_graph, node)
            
            self.node_order.append(node)
            processed_nodes.add(node)
            count += 1
            if count % 500 == 0:
                print(f"  Nodi contratti: {count}/{total_nodes}...")
            
            # --- AGGIORNAMENTO DEI VICINI ---
            # Dopo aver contratto `node`, le priorità dei suoi vicini sono cambiate.
            # Dobbiamo ricalcolarle e aggiornarle nella coda.
            neighbors_to_update = set(contraction_graph.neighbors(node, mode='all'))
            for neighbor in neighbors_to_update:
                if neighbor not in processed_nodes:
                    new_priority = self._calculate_priority(contraction_graph, neighbor)
                    priorities[neighbor] = new_priority
                    heapq.heappush(priority_queue, (new_priority, neighbor))

        self.node_levels = {node: i for i, node in enumerate(self.node_order)}
        self.shortcut_graph = contraction_graph
        self.shortcut_graph.es['middle_node'] = [None] * self.shortcut_graph.ecount()
        
        # Ricostruiamo il grafo finale con gli shortcut per la query
        final_graph = self.original_graph.copy()
        final_graph.es['middle_node'] = [None] * final_graph.ecount()
        final_graph.add_edges(
            [(e.source, e.target) for e in self.shortcut_graph.es if 'middle_node' in e.attributes() and e['middle_node'] is not None],
            attributes={'weight': [e['weight'] for e in self.shortcut_graph.es if 'middle_node' in e.attributes() and e['middle_node'] is not None],
                        'middle_node': [e['middle_node'] for e in self.shortcut_graph.es if 'middle_node' in e.attributes() and e['middle_node'] is not None]}
        )
        self.shortcut_graph = final_graph

        end_time = time.time()
        self.preprocessing_time = (end_time - start_time) * 1000
        self.space_preprocessing_bytes = self.dataUtils.get_deep_size(self.shortcut_graph.get_edgelist())

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
        forward_dist = {node: float('inf') for node in range(self.original_graph.vcount())}
        backward_dist = {node: float('inf') for node in range(self.original_graph.vcount())}
        forward_dist[start_node] = 0
        backward_dist[end_node] = 0
        forward_prev = {node: None for node in range(self.original_graph.vcount())}
        backward_prev = {node: None for node in range(self.original_graph.vcount())}
        forward_queue = [(0, start_node)]
        backward_queue = [(0, end_node)]
        min_dist = float('inf')
        meeting_node = -1
        explored_nodes = 0

        while forward_queue or backward_queue:
            if forward_queue and backward_queue:
                if forward_queue[0][0] + backward_queue[0][0] >= min_dist: break
            
            if forward_queue and (not backward_queue or forward_queue[0][0] <= backward_queue[0][0]):
                dist_f, u = heapq.heappop(forward_queue)
                explored_nodes += 1
                if backward_dist.get(u, float('inf')) != float('inf'):
                    current_dist = dist_f + backward_dist[u]
                    if current_dist < min_dist:
                        min_dist = current_dist
                        meeting_node = u
                for v_id in self.shortcut_graph.neighbors(u, mode="out"):
                    if self.node_levels.get(v_id, -1) > self.node_levels.get(u, -1):
                        eid = self.shortcut_graph.get_eid(u, v_id)
                        weight = self.shortcut_graph.es[eid]['weight']
                        if forward_dist.get(u, float('inf')) + weight < forward_dist.get(v_id, float('inf')):
                            forward_dist[v_id] = forward_dist[u] + weight
                            forward_prev[v_id] = u
                            heapq.heappush(forward_queue, (forward_dist[v_id], v_id))
            elif backward_queue:
                dist_b, u = heapq.heappop(backward_queue)
                explored_nodes += 1
                if forward_dist.get(u, float('inf')) != float('inf'):
                    current_dist = dist_b + forward_dist[u]
                    if current_dist < min_dist:
                        min_dist = current_dist
                        meeting_node = u
                for v_id in self.shortcut_graph.neighbors(u, mode="in"):
                    if self.node_levels.get(v_id, -1) > self.node_levels.get(u, -1):
                        eid = self.shortcut_graph.get_eid(v_id, u)
                        weight = self.shortcut_graph.es[eid]['weight']
                        if backward_dist.get(u, float('inf')) + weight < backward_dist.get(v_id, float('inf')):
                            backward_dist[v_id] = backward_dist[u] + weight
                            backward_prev[v_id] = u
                            heapq.heappush(backward_queue, (backward_dist[v_id], v_id))
            else:
                break
        
        path = []
        if meeting_node != -1:
            shortcut_path_forward = []
            curr = meeting_node
            while curr is not None:
                shortcut_path_forward.append(curr)
                curr = forward_prev.get(curr)
            shortcut_path_forward.reverse()
            shortcut_path_backward = []
            curr = backward_prev.get(meeting_node)
            while curr is not None:
                shortcut_path_backward.append(curr)
                curr = backward_prev.get(curr)
            shortcut_path = shortcut_path_forward + shortcut_path_backward
            if shortcut_path:
                path = [shortcut_path[0]]
                for i in range(len(shortcut_path) - 1):
                    u, v = shortcut_path[i], shortcut_path[i+1]
                    unpacked_segment = self._unpack_path(u, v)
                    path.extend(unpacked_segment[1:])

        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        query_space = (self.dataUtils.get_deep_size(forward_dist) + self.dataUtils.get_deep_size(backward_dist) + 
                       self.dataUtils.get_deep_size(forward_prev) + self.dataUtils.get_deep_size(backward_prev))

        return {
            'graph_name': 'N/A',
            'tot nodes': self.original_graph.vcount(),
            'start_node': start_node,
            'end_node': end_node,
            'preprocessing_time (ms)': self.preprocessing_time,
            'execution_time (ms)': elapsed_time if min_dist != float('inf') else -1,
            'explored_nodes': explored_nodes,
            'path_weight': min_dist if min_dist != float('inf') else -1,
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

