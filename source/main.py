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

def verify_and_plot_path():
    """
    Calcola un singolo percorso su un grafo reale e lo visualizza.
    """
    print("\n--- Verifica e Visualizzazione Percorso su Grafo Reale ---")
    try:
        city_query = input("Inserisci la città per il test (es. 'L'Aquila, Italy' o 'Rome, Italy'): ")
        graph = real_graphs.RealGraph(city_query)
        
        start_node = int(input(f"Inserisci il nodo di partenza (0-{graph.graph.vcount()-1}): "))
        end_node = int(input(f"Inserisci il nodo di arrivo (0-{graph.graph.vcount()-1}): "))

        if not (0 <= start_node < graph.graph.vcount() and 0 <= end_node < graph.graph.vcount()):
            print("Errore: Nodi non validi.")
            return

        # Esegui Dijkstra per ottenere il percorso di riferimento
        dijkstra_algo = dj.Dijkstra()
        dijkstra_result = dijkstra_algo.run(graph, 1, [start_node], [end_node])[0]
        
        # Esegui CH per confrontare il peso
        ch_algo = ch.Contraction_Hierarchies()
        ch_result = ch_algo.run(graph, 1, [start_node], [end_node])[0]
        
        print("\n--- Risultati Confrontati ---")
        print(f"Dijkstra Path Weight: {dijkstra_result['path_weight']:.2f}")
        print(f"CH Path Weight:       {ch_result['path_weight']:.2f}")

        if abs(dijkstra_result['path_weight'] - ch_result['path_weight']) < 1e-6:
            print("VALIDAZIONE: I pesi dei percorsi corrispondono.")
        else:
            print("ATTENZIONE: I pesi dei percorsi NON corrispondono.")

        # Visualizza il percorso sulla mappa
        graph.plot_graph(path=dijkstra_result['path'], start_node=start_node, end_node=end_node)

    except Exception as e:
        print(f"Si è verificato un errore: {e}")

def run_random_graph_correctness_test():
    """
    Esegue un test mirato su un grafo random per verificare la correttezza confrontando i risultati.
    """
    print("\n--- Test di Correttezza su Grafo Random ---")
    try:
        num_nodes = int(input("Inserisci il numero di nodi per il grafo random: "))
        density = float(input("Inserisci la densità (es. 0.01): "))
        seed = int(input("Inserisci un seed per la riproducibilità (es. 42): "))

        graph = random_graphs.Random_Graph(num_nodes, density, seed)
        
        start_node = int(input(f"Inserisci il nodo di partenza (0-{num_nodes-1}): "))
        end_node = int(input(f"Inserisci il nodo di arrivo (0-{num_nodes-1}): "))

        if not (0 <= start_node < num_nodes and 0 <= end_node < num_nodes):
            print("Errore: Nodi non validi.")
            return

        # Esegui Dijkstra
        dijkstra_algo = dj.Dijkstra()
        dijkstra_result = dijkstra_algo.run(graph, 1, [start_node], [end_node])[0]
        
        # Esegui CH
        ch_algo = ch.Contraction_Hierarchies()
        ch_result = ch_algo.run(graph, 1, [start_node], [end_node])[0]
        
        print("\n--- Risultati del Test di Correttezza ---")
        print(f"Query: {start_node} -> {end_node}")
        
        print("\n[DIJKSTRA]")
        print(f"  - Peso del percorso: {dijkstra_result['path_weight']:.2f}")
        print(f"  - Percorso (nodi): {dijkstra_result['path']}")
        
        print("\n[CONTRACTION HIERARCHIES]")
        print(f"  - Peso del percorso: {ch_result['path_weight']:.2f}")
        print(f"  - Percorso (nodi): {ch_result['path']}")

        print("\n--- VERIFICA ---")
        if abs(dijkstra_result['path_weight'] - ch_result['path_weight']) < 1e-6:
            print("OK: I pesi dei percorsi calcolati dai due algoritmi corrispondono.")
        else:
            print("!!! ERRORE: I pesi dei percorsi NON corrispondono. !!!")
            
        if dijkstra_result['path'] == ch_result['path']:
             print("OK: Le liste di nodi dei percorsi corrispondono.")
        else:
             print("ATTENZIONE: Le liste di nodi dei percorsi NON corrispondono.")

    except Exception as e:
        print(f"Si è verificato un errore durante il test: {e}")

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
     print("4. verifica e visualizza percorso")
     print("5. Test di correttezza su un grafo random")
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
          main_menu('7')  # Pass '7' to run all analyses automatically
     elif choice == '4':
          verify_and_plot_path()
     elif choice == '5':
          run_random_graph_correctness_test()
     elif choice == '6':
          print("Uscita.")
     else:
         print("Invalid choice. Exiting.")
         return

if __name__ == "__main__":
    main()