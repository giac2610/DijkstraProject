# Struttura del main:
# - scelta del tipo di grafo
     # - dataset Random
     # - dataset Real
# - parametri del grafo random
     # - numero di nodi
     # - densità
     # - randomizzazione del seed
# - esecuzione dei due algoritmi su stesso grafo
     # - numero di query
     # - randomizzare nodi partenza e arrivo
     # - calcolo del tempo di esecuzione 
     # - calcolo nodi esplorati
     # - calcolo di pre-processing solo per CH
# - salva risultati su CSV
# - plot dei risultati

import numpy as np
from graphs import random_graphs, real_graphs
from algorithms import djikstra as dj
from algorithms import d_contraction_hierarchies as ch
from utils import utils

def run_single_experiment(graph_obj, graph_name, num_queries, dijkstra, ch_algo):
     """
     Esegue un singolo esperimento (Dijkstra vs CH) su un dato grafo.
     Restituisce i risultati per entrambi gli algoritmi.
     """
     print(f"\n--- Inizio esperimento su: {graph_name} ---")
     print(f"Numero di nodi: {graph_obj.graph.vcount()}, Numero di archi: {graph_obj.graph.ecount()}")

     # Genera un set fisso di query per la riproducibilità
     start_node_list, end_node_list = [], []
     for _ in range(num_queries):
          start_node = graph_obj.get_random_node()
          end_node = graph_obj.get_random_node(start_node)
          start_node_list.append(start_node)
          end_node_list.append(end_node)

     # Esegui gli algoritmi
     print(f"Esecuzione di {num_queries} query...")
     dijkstra_results = dijkstra.run(graph_obj, num_queries, start_node_list, end_node_list)
     ch_results = ch_algo.run(graph_obj, num_queries, start_node_list, end_node_list)

     # Aggiungi il nome del grafo a ogni risultato per l'analisi aggregata
     for res in dijkstra_results:
          res['graph_name'] = graph_name
          res['queries'] = num_queries
     for res in ch_results:
          res['graph_name'] = graph_name
          res['queries'] = num_queries
     
     print(f"--- Esperimento su {graph_name} completato ---")
     return dijkstra_results, ch_results

def main():
     print("Algorithm Comparison Tool")
     print("Initialization...")
     dijkstra = dj.Dijkstra()
     contraction_hierarchies = ch.Contraction_Hierarchies()
     raw_data = utils.RawData()
     print("Choose the type of graph:")
     print("1. Interactive Random Graph")
     print("2. Real Graph")
     print("3. Full Test")
     choice = input("Enter your choice (1, 2 or 3): ")
     if choice == '1':
          test_name = "Test 1"
          num_nodes = int(input("Enter number of nodes: "))
          density = float(input("Enter density (0-1): "))
          graph = random_graphs.Random_Graph(num_nodes, density, seed=42)
          d_res, ch_res = run_single_experiment(graph, f"Random_{num_nodes}", 100, dijkstra, contraction_hierarchies)
          raw_data.save_to_csv('dijkstra_interactive_results.csv', d_res)
          raw_data.save_to_csv('ch_interactive_results.csv', ch_res)
          print("Risultati salvati.")
               
     elif choice == '2':
          test_name = "Test 2"
          place_name = 'L\'Aquila, Abruzzo, Italy'
          graph = real_graphs.RealGraph(place_name)
          d_res, ch_res = run_single_experiment(graph, place_name.split(',')[0], 100, dijkstra, contraction_hierarchies)
          raw_data.save_to_csv('dijkstra_interactive_results.csv', d_res)
          raw_data.save_to_csv('ch_interactive_results.csv', ch_res)
          print("Risultati salvati.")
     elif choice == '3':
          test_name = "Test 3"
          print("\n===== Avvio Full Test Suite =====")
          # Liste separate per i risultati
          random_dijkstra_results = []
          random_ch_results = []
          real_dijkstra_results = []
          real_ch_results = []
          NUM_QUERIES_PER_REAL_TEST = 250

          # --- Test su Grafi Random ---
          print("\n[PARTE 1] Test su grafi random di dimensioni crescenti...")
          node_steps = np.linspace(500, 15000, 5, dtype=int)
          for num_nodes in node_steps:
               for avg_degree in [1.5, 2.5, 3.5]:
                    for query_num in [50, 150, 500]:
                         density = avg_degree / num_nodes
                         
                         graph = random_graphs.Random_Graph(num_nodes, density, seed=42)
                         graph_name = f"Random_{num_nodes}_nodes_deg_{avg_degree}_queries_{query_num}"
                         
                         d_res, ch_res = run_single_experiment(graph, graph_name, query_num, dijkstra, contraction_hierarchies)
                         random_dijkstra_results.extend(d_res)
                         random_ch_results.extend(ch_res)
          
          # --- Test su Grafi Reali ---
          print("\n[PARTE 2] Test su grafi stradali reali...")
          cities = ["L'Aquila, Abruzzo, Italy", "Rome, Lazio, Italy", "Milan, Lombardia, Italy"]

          for city in cities:
               try:
                    graph = real_graphs.RealGraph(city)
                    graph_name = city.split(',')[0]
                    
                    d_res, ch_res = run_single_experiment(graph, graph_name, NUM_QUERIES_PER_REAL_TEST, dijkstra, contraction_hierarchies)
                    real_dijkstra_results.extend(d_res)
                    real_ch_results.extend(ch_res)
               except Exception as e:
                    print(f"ERRORE: Impossibile scaricare o processare il grafo per {city}. Dettagli: {e}")
                    print("Continuo con il prossimo test...")

          # --- Salvataggio dei risultati in file separati ---
          print("\n[PARTE 3] Salvataggio dei risultati aggregati...")
          # print(random_dijkstra_results)
          # print(real_dijkstra_results)
          if random_dijkstra_results:
               raw_data.save_to_csv('RANDOM_TESTS_dijkstra_results.csv', random_dijkstra_results)
               raw_data.save_to_csv('RANDOM_TESTS_ch_results.csv', random_ch_results)
          if real_dijkstra_results:
               raw_data.save_to_csv('REAL_TESTS_dijkstra_results.csv', real_dijkstra_results)
               raw_data.save_to_csv('REAL_TESTS_ch_results.csv', real_ch_results)
          
          print("\n===== Full Test Suite Completato! =====")
          print("I tuoi dati sono pronti per l'analisi nei file:")
          print("- RANDOM_TESTS_dijkstra_results.csv")
          print("- RANDOM_TESTS_ch_results.csv")
          print("- REAL_TESTS_dijkstra_results.csv")
          print("- REAL_TESTS_ch_results.csv")
          
          # plot all the analysis automatically
          
          from analysis import main_menu
          main_menu(7)  # Pass '7' to run all analyses automatically
          
     else:
         print("Invalid choice. Exiting.")
         return

if __name__ == "__main__":
    main()