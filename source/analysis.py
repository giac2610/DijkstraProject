import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid")

RESULTS_DIR = 'results'

def load_data():
    try:
        random_dijkstra = pd.read_csv(os.path.join(RESULTS_DIR, 'RANDOM_TESTS_dijkstra_results.csv'))
        random_ch = pd.read_csv(os.path.join(RESULTS_DIR, 'RANDOM_TESTS_ch_results.csv'))
        real_dijkstra = pd.read_csv(os.path.join(RESULTS_DIR, 'REAL_TESTS_dijkstra_results.csv'))
        real_ch = pd.read_csv(os.path.join(RESULTS_DIR, 'REAL_TESTS_ch_results.csv'))
        return random_dijkstra, random_ch, real_dijkstra, real_ch
    except FileNotFoundError as e:
        print(f"ERRORE: File non trovato - {e}.")
        print("Assicurati di aver eseguito il 'Full Test Suite' (opzione 3 in main.py) prima di lanciare l'analisi.")
        return None

def plot_performance_vs_size(random_dijkstra, random_ch):
    print("Elaborazione grafici: Performance vs. Dimensione del Grafo...")

    random_dijkstra['num_nodes'] = random_dijkstra['graph_name'].str.split('_').str[1].astype(int)
    random_ch['num_nodes'] = random_ch['graph_name'].str.split('_').str[1].astype(int)

    # Calcoliamo i valori medi per ogni dimensione del grafo
    avg_dijkstra = random_dijkstra.groupby('num_nodes')['execution_time (ms)'].mean().reset_index()
    avg_ch_query = random_ch.groupby('num_nodes')['execution_time (ms)'].mean().reset_index()
    avg_ch_prep = random_ch.groupby('num_nodes')['preprocessing_time (ms)'].mean().reset_index()

    # Grafico 1: Tempo di Query
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=avg_dijkstra, x='num_nodes', y='execution_time (ms)', marker='o', label='Dijkstra (Query)')
    sns.lineplot(data=avg_ch_query, x='num_nodes', y='execution_time (ms)', marker='o', label='CH (Query)')
    plt.title('Tempo di Query vs. Dimensione del Grafo (Random)', fontsize=16)
    plt.xlabel('Numero di Nodi', fontsize=12)
    plt.ylabel('Tempo Medio di Esecuzione (ms)', fontsize=12)
    plt.legend()
    plt.savefig(os.path.join(RESULTS_DIR, 'plot_query_time_vs_size.png'))
    print(f"Grafico salvato in: {os.path.join(RESULTS_DIR, 'plot_query_time_vs_size.png')}")
    plt.close()

    # Grafico 2: Tempo di Pre-processing di CH
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=avg_ch_prep, x='num_nodes', y='preprocessing_time (ms)', marker='o', color='green', label='CH (Pre-processing)')
    plt.title('Tempo di Pre-processing CH vs. Dimensione del Grafo (Random)', fontsize=16)
    plt.xlabel('Numero di Nodi', fontsize=12)
    plt.ylabel('Tempo Medio di Pre-processing (ms)', fontsize=12)
    plt.legend()
    plt.savefig(os.path.join(RESULTS_DIR, 'plot_preprocessing_time_vs_size.png'))
    print(f"Grafico salvato in: {os.path.join(RESULTS_DIR, 'plot_preprocessing_time_vs_size.png')}")
    plt.close()

def plot_performance_on_real(real_dijkstra, real_ch):
    print("Elaborazione grafici: Performance su Grafi Reali...")

    avg_dijkstra = real_dijkstra.groupby('graph_name')['execution_time (ms)'].mean().reset_index()
    avg_dijkstra['Algorithm'] = 'Dijkstra'
    avg_ch = real_ch.groupby('graph_name')['execution_time (ms)'].mean().reset_index()
    avg_ch['Algorithm'] = 'CH'
    
    combined = pd.concat([avg_dijkstra, avg_ch])

    plt.figure(figsize=(12, 7))
    sns.barplot(data=combined, x='graph_name', y='execution_time (ms)', hue='Algorithm')
    plt.title('Tempo Medio di Query su Grafi Reali (Città)', fontsize=16)
    plt.xlabel('Città', fontsize=12)
    plt.ylabel('Tempo Medio di Esecuzione (ms)', fontsize=12)
    plt.yscale('log')
    plt.legend(title='Algoritmo')
    plt.savefig(os.path.join(RESULTS_DIR, 'plot_query_time_real_graphs.png'))
    print(f"Grafico salvato in: {os.path.join(RESULTS_DIR, 'plot_query_time_real_graphs.png')}")
    plt.close()

def plot_explored_nodes(random_dijkstra, random_ch, real_dijkstra, real_ch):
    """Genera grafici a barre per confrontare i nodi esplorati."""
    print("Elaborazione grafici: Nodi Esplorati...")

    avg_dijkstra_real = real_dijkstra.groupby('graph_name')['explored_nodes'].mean().reset_index()
    avg_dijkstra_real['Algorithm'] = 'Dijkstra'
    avg_ch_real = real_ch.groupby('graph_name')['explored_nodes'].mean().reset_index()
    avg_ch_real['Algorithm'] = 'CH'
    combined_real = pd.concat([avg_dijkstra_real, avg_ch_real])
    
    plt.figure(figsize=(12, 7))
    sns.barplot(data=combined_real, x='graph_name', y='explored_nodes', hue='Algorithm')
    plt.title('Numero Medio di Nodi Esplorati (Grafi Reali)', fontsize=16)
    plt.xlabel('Città', fontsize=12)
    plt.ylabel('Nodi Esplorati per Query (Scala Log)', fontsize=12)
    plt.yscale('log')
    plt.legend(title='Algoritmo')
    plt.savefig(os.path.join(RESULTS_DIR, 'plot_explored_nodes_real_graphs.png'))
    print(f"Grafico salvato in: {os.path.join(RESULTS_DIR, 'plot_explored_nodes_real_graphs.png')}")
    plt.close()

def main_menu():
    data = load_data()
    if not data:
        return

    random_dijkstra, random_ch, real_dijkstra, real_ch = data

    while True:
        print("\n--- Menu di Analisi e Plotting ---")
        print("1. Genera grafici: Performance vs. Dimensione (Grafi Random)")
        print("2. Genera grafici: Performance su Città (Grafi Reali)")
        print("3. Genera grafici: Confronto Nodi Esplorati (Grafi Reali)")
        print("4. Esegui tutte le analisi e genera tutti i grafici")
        print("5. Esci")
        
        choice = input("Scegli un'opzione (1-5): ")

        if choice == '1':
            plot_performance_vs_size(random_dijkstra, random_ch)
        elif choice == '2':
            plot_performance_on_real(real_dijkstra, real_ch)
        elif choice == '3':
            plot_explored_nodes(random_dijkstra, random_ch, real_dijkstra, real_ch)
        elif choice == '4':
            print("\nEsecuzione di tutte le analisi...")
            plot_performance_vs_size(random_dijkstra, random_ch)
            plot_performance_on_real(real_dijkstra, real_ch)
            plot_explored_nodes(random_dijkstra, random_ch, real_dijkstra, real_ch)
            print("\n--- Analisi Completata ---")
            print(f"Tutti i grafici sono stati salvati nella cartella '{RESULTS_DIR}'.")
        elif choice == '5':
            print("Uscita.")
            break
        else:
            print("Scelta non valida. Riprova.")

if __name__ == '__main__':
    main_menu()
