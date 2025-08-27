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

from graphs import random_graphs, real_graphs
from algorithms import djikstra as dj
from algorithms import d_contraction_hierarchies as ch
from utils import utils

def main():
     print("Algorithm Comparison Tool")
     print("Initialization...")
     dijkstra = dj.Dijkstra()
     contraction_hierarchies = ch.Contraction_Hierarchies()
     raw_data = utils.RawData()
     print("Choose the type of graph:")
     print("1. Random Graph")
     print("2. Real Graph")
     choice = input("Enter your choice (1 or 2): ")
     if choice == '1':
          # Handle random graph
          num_nodes = int(input("Enter number of nodes: "))
          density = float(input("Enter density (0-1): "))
          print("choose if you wasnt a random seed or not:")
          random_seed = input("personalized seed? (y/n): ").strip().lower()
          randomize = random_seed == 'y'
          seed = None
          if randomize:
               seed = int(input("Enter your seed: "))
               print(f"Using seed: {seed}")
          else:
               print("Using default seed.")
               # utils.getRandomSeed()
          print(f"Generating random graph with {num_nodes} nodes and density {density}, with  {'selected seed' if seed is not None else 'default seed'}")
          graph = random_graphs.Random_Graph(num_nodes, density, seed)
 
          print("choose the number of queries")
          num_queries = int(input("Enter number of queries: "))
          
          start_node_list, end_node_list = [], []
          for _ in range(num_queries):
               start_node = graph.get_random_node()
               end_node = graph.get_random_node(start_node)
               start_node_list.append(start_node)
               end_node_list.append(end_node)
          
          
          dijkstra.run(graph, num_queries, start_node_list, end_node_list)
          contraction_hierarchies.run(graph, num_queries, start_node_list, end_node_list)

          # load results from CSV files
          dijkstra_results = raw_data.load_dijkstra_results()
          ch_results = raw_data.load_ch_results()
          
          # plot the results
          raw_data.plot_and_analyze(dijkstra_results, ch_results)
          
     elif choice == '2':
          # TODO: Handle real graph
          pass
     else:
         print("Invalid choice. Exiting.")
         return

if __name__ == "__main__":
    main()