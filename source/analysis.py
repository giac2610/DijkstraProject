import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Imposta uno stile grafico gradevole
sns.set_theme(style="whitegrid")

# Definisci la cartella dei risultati
RESULTS_DIR = 'results'

def load_data():
    """Carica tutti i file CSV necessari per l'analisi."""
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

def plot_performance_vs_size(df_dijkstra, df_ch):

     random_dijkstra = df_dijkstra.copy()
     random_ch = df_ch.copy()
     """Genera grafici che confrontano le performance al variare del numero di nodi."""
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

def plot_performance_on_real(df_dijkstra, df_ch):

    real_dijkstra = df_dijkstra.copy()
    real_ch = df_ch.copy()
    """Genera un bar plot per le performance sui grafi reali (città)."""
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

def plot_explored_nodes(df_dijkstra, df_ch):
     
    real_dijkstra = df_dijkstra.copy()
    real_ch = df_ch.copy()
    """Genera grafici a barre per confrontare i nodi esplorati sui grafi reali."""
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

# NUOVA FUNZIONE
def plot_performance_vs_degree(df_dijkstra, df_ch):
     
    """
    Analizza e plotta l'impatto della densità del grafo (grado medio) 
    sulle performance degli algoritmi.
    """
    random_dijkstra = df_dijkstra.copy()
    random_ch = df_ch.copy()
    print("Elaborazione grafici: Performance vs. Densità del Grafo...")

    # Aggiungi una colonna per identificare l'algoritmo
    random_dijkstra['algorithm'] = 'Dijkstra'
    random_ch['algorithm'] = 'Contraction Hierarchies'
    
    # Rinomina colonne per coerenza
    random_dijkstra.rename(columns={'execution_time (ms)': 'Execution Time'}, inplace=True)
    random_ch.rename(columns={'execution_time (ms)': 'Execution Time'}, inplace=True)

    # Concatena i due DataFrame
    df_all = pd.concat([random_dijkstra, random_ch], ignore_index=True)
    
    # Estrai numero di nodi e grado medio dal nome del grafo
    df_all['num_nodes'] = df_all['graph_name'].apply(lambda x: int(x.split('_')[1]))
    df_all['avg_degree'] = df_all['graph_name'].apply(lambda x: float(x.split('_')[4]))

    # Aggrega i dati calcolando la media
    df_agg = df_all.groupby(['num_nodes', 'avg_degree', 'algorithm'])['Execution Time'].mean().reset_index()

    # Crea il grafico con FacetGrid per separare i plot per grado medio
    g = sns.FacetGrid(df_agg, col="avg_degree", hue="algorithm", col_wrap=3, 
                      height=5, aspect=1.2, palette=["#ff7f0e", "#1f77b4"], sharey=False)

    g.map(plt.plot, "num_nodes", "Execution Time", marker="o", alpha=0.8)
    g.set_axis_labels("Numero di Nodi", "Tempo Medio di Esecuzione (ms)")
    g.set_titles("Grado Medio = {col_name}")
    g.add_legend(title="Algoritmo")
    g.fig.suptitle("Performance vs. Nodi e Densità del Grafo", y=1.03, fontsize=16)

    plt.savefig(os.path.join(RESULTS_DIR, 'plot_performance_vs_degree.png'), bbox_inches='tight')
    print(f"Grafico salvato in: {os.path.join(RESULTS_DIR, 'plot_performance_vs_degree.png')}")
    plt.close()

def plot_performance_vs_queries(df_dijkstra, df_ch):
    """
    Analizza e plotta come il tempo di esecuzione totale scala
    al variare del numero di query eseguite.
    """
    random_dijkstra = df_dijkstra.copy()
    random_ch = df_ch.copy()
    print("Elaborazione grafici: Performance vs. Numero di Query...")

    # Combina i dati e rinomina le colonne per semplicità
    random_dijkstra['algorithm'] = 'Dijkstra'
    random_ch['algorithm'] = 'CH'
    df_all = pd.concat([random_dijkstra, random_ch], ignore_index=True)
    df_all.rename(columns={'execution_time (ms)': 'Execution Time'}, inplace=True)
    
    # Estrai i parametri. Assumiamo che 'num_queries' sia presente nel CSV.
    if 'num_queries' not in df_all.columns:
        print("ERRORE: La colonna 'num_queries' non è presente nei file CSV.")
        print("Assicurati di aver modificato main.py e rieseguito il Full Test.")
        return
        
    df_all['num_nodes'] = df_all['graph_name'].apply(lambda x: int(x.split('_')[1]))

    # Aggreghiamo: calcoliamo il tempo MEDIO per query per ogni gruppo
    df_agg = df_all.groupby(['num_nodes', 'num_queries', 'algorithm'])['Execution Time'].mean().reset_index()

    # Creazione del grafico
    g = sns.FacetGrid(df_agg, col="num_nodes", hue="algorithm", col_wrap=3,
                      height=5, aspect=1.2, palette=["#ff7f0e", "#1f77b4"], sharey=False)
    
    g.map(plt.plot, "num_queries", "Execution Time", marker="o", alpha=0.8)
    g.set_axis_labels("Numero di Query Eseguite", "Tempo Medio per Query (ms)")
    g.set_titles("Nodi = {col_name}")
    g.add_legend(title="Algoritmo")
    g.fig.suptitle("Scalabilità degli Algoritmi vs. Numero di Query", y=1.03, fontsize=16)

    plt.savefig(os.path.join(RESULTS_DIR, 'plot_performance_vs_queries.png'), bbox_inches='tight')
    print(f"Grafico salvato in: {os.path.join(RESULTS_DIR, 'plot_performance_vs_queries.png')}")
    plt.close()



# NUOVA FUNZIONE
def plot_breakeven_point(df_dijkstra, df_ch, df_real_dijkstra, df_real_ch):
    """
    Calcola e visualizza il numero di query necessarie affinché CH diventi
    più conveniente di Dijkstra, considerando il tempo di pre-processing.
    """
    random_dijkstra = df_dijkstra.copy()
    random_ch = df_ch.copy()
    print("Elaborazione grafici: Analisi del Breakeven Point...")

    # Estrai i parametri e rinomina le colonne
    random_dijkstra['num_nodes'] = random_dijkstra['graph_name'].str.split('_').str[1].astype(int)
    random_dijkstra['avg_degree'] = random_dijkstra['graph_name'].str.split('_').str[4].astype(float)
    random_ch['num_nodes'] = random_ch['graph_name'].str.split('_').str[1].astype(int)
    random_ch['avg_degree'] = random_ch['graph_name'].str.split('_').str[4].astype(float)

    # Aggrega i dati calcolando le medie
    avg_dijkstra = random_dijkstra.groupby(['num_nodes', 'avg_degree'])['execution_time (ms)'].mean().reset_index()
    avg_dijkstra.rename(columns={'execution_time (ms)': 'dijkstra_query_time'}, inplace=True)

    avg_ch = random_ch.groupby(['num_nodes', 'avg_degree']).agg(
        ch_query_time=('execution_time (ms)', 'mean'),
        ch_prep_time=('preprocessing_time (ms)', 'mean')
    ).reset_index()

    df_merged = pd.merge(avg_dijkstra, avg_ch, on=['num_nodes', 'avg_degree'])

    # Calcola il breakeven point (N queries)
    # N = T_prep / (T_dijkstra - T_ch)
    time_diff = df_merged['dijkstra_query_time'] - df_merged['ch_query_time']
    
    # Evita divisione per zero se T_ch >= T_dijkstra
    df_merged['breakeven_queries'] = np.where(
        time_diff > 0,
        df_merged['ch_prep_time'] / time_diff,
        np.inf
    )

    # Creazione del grafico random
    plt.figure(figsize=(14, 8))
    sns.barplot(data=df_merged, x='num_nodes', y='breakeven_queries', hue='avg_degree', palette='viridis')
    
    plt.title('Breakeven Point: Numero di Query per Ammortizzare il Pre-processing di CH', fontsize=16)
    plt.xlabel('Dimensione del Grafo (Numero di Nodi)', fontsize=12)
    plt.ylabel('Numero di Query (Breakeven Point)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title='Grado Medio')
    plt.tight_layout()

    plt.savefig(os.path.join(RESULTS_DIR, 'plot_breakeven_analysis.png'))
    print(f"Grafico salvato in: {os.path.join(RESULTS_DIR, 'plot_breakeven_analysis.png')}")
    plt.close()

    # Analisi del breakeven point per i grafi reali
    real_ch = df_real_ch.copy()
    real_dijkstra = df_real_dijkstra.copy()
    print("Elaborazione grafici: Analisi del Breakeven Point (Grafi Reali)...")

    avg_dijkstra = real_dijkstra.groupby('graph_name')['execution_time (ms)'].mean().reset_index()
    avg_dijkstra.rename(columns={'execution_time (ms)': 'dijkstra_query_time'}, inplace=True)
    avg_ch = real_ch.groupby('graph_name').agg(
        ch_query_time=('execution_time (ms)', 'mean'),
        ch_prep_time=('preprocessing_time (ms)', 'mean')
    ).reset_index()
    df_merged = pd.merge(avg_dijkstra, avg_ch, on='graph_name')
    time_diff = df_merged['dijkstra_query_time'] - df_merged['ch_query_time']
    df_merged['breakeven_queries'] = np.where(time_diff > 0, df_merged['ch_prep_time'] / time_diff, np.inf)

    plt.figure(figsize=(12, 7))
    sns.barplot(data=df_merged, x='graph_name', y='breakeven_queries', palette='plasma')
    plt.title('Breakeven Point: Numero di Query per Ammortizzare il Pre-processing di CH (Grafi Reali)', fontsize=16)
    plt.xlabel('Città', fontsize=12)
    plt.ylabel('Numero di Query (Breakeven Point)', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'plot_breakeven_analysis_real.png'))
    plt.close()


def main_menu(choice = None):
    data = load_data()
    if not data:
        return

    random_dijkstra, random_ch, real_dijkstra, real_ch = data

    while True:
        print("\n--- Menu di Analisi e Plotting ---")
        print("1. Genera grafici: Performance vs. Dimensione (Grafi Random)")
        print("2. Genera grafici: Performance su Città (Grafi Reali)")
        print("3. Genera grafici: Confronto Nodi Esplorati (Grafi Reali)")
        print("4. Genera grafici: Performance vs. Densità (Grafi Random)")
        print("5. Grafici: Performance vs. Numero di Query (Random)")
        print("6. Analisi del Breakeven Point")
        print("7. Esegui tutte le analisi")
        print("8. Esci")
        if choice is None:
          choice = input("Scegli un'opzione (1-8): ")

        if choice == '1':
            plot_performance_vs_size(random_dijkstra, random_ch)
        elif choice == '2':
            plot_performance_on_real(real_dijkstra, real_ch)
        elif choice == '3':
            plot_explored_nodes(real_dijkstra, real_ch)
        elif choice == '4':
            plot_performance_vs_degree(random_dijkstra, random_ch)
        elif choice == '5':
            plot_performance_vs_queries(random_dijkstra, random_ch)
        elif choice == '6':
            plot_breakeven_point(random_dijkstra, random_ch)
        elif choice == '7':
            print("\nEsecuzione di tutte le analisi...")
            plot_performance_vs_size(random_dijkstra, random_ch)
            plot_performance_on_real(real_dijkstra, real_ch)
            plot_explored_nodes(real_dijkstra, real_ch)
            plot_performance_vs_degree(random_dijkstra, random_ch)
            plot_performance_vs_queries(random_dijkstra, random_ch)
            plot_breakeven_point(random_dijkstra, random_ch, real_dijkstra, real_ch)
            print("\n--- Analisi Completata ---")
            print(f"Tutti i grafici sono stati salvati nella cartella '{RESULTS_DIR}'.")
            break
        elif choice == '8':
            print("Uscita.")
            break
        else:
            print("Scelta non valida. Riprova.")

if __name__ == '__main__':
    # Assicurati che la cartella dei risultati esista
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        print(f"Cartella '{RESULTS_DIR}' creata.")
    main_menu()