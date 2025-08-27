import sys
import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore

class RawData:
    def __init__(self):
        pass

    def save_to_csv(self, filename, data):
        import csv
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = data[0].keys() if data else []
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"Data saved to {filename}")
    
    import sys

    def get_deep_size(self, obj, seen=None):
        
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([self.get_deep_size(v, seen) for v in obj.values()])
            size += sum([self.get_deep_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([self.get_deep_size(i, seen) for i in obj])
        return size

    def load_dijkstra_results(self):
        return pd.read_csv('dijkstra_results.csv')
    
    def load_ch_results(self):
        return pd.read_csv('contraction_hieraarchies_results.csv')
    
    def plot_and_analyze(dijkstra_file, ch_file):
        """
        Carica i dati, genera grafici di confronto e calcola i tempi totali.
        """
        # Caricare i dataset
        df_dijkstra = pd.read_csv(dijkstra_file)
        df_ch = pd.read_csv(ch_file)

        # --- Pulizia dei Nomi delle Colonne ---
        df_dijkstra.rename(columns={
            'execution_time (ms)': 'execution_time_ms',
            'explored_nodes': 'explored_nodes',
            'space_occupation (Byte):': 'space_query_byte'
        }, inplace=True)

        df_ch.rename(columns={
            'execution_time (ms)': 'execution_time_ms',
            'explored_nodes': 'explored_nodes',
            'space_query (Byte)': 'space_query_byte',
            'preprocessing_time (ms)': 'preprocessing_time_ms'
        }, inplace=True)
        
        # Selezionare solo le colonne rilevanti
        cols_dijkstra = ['start_node', 'end_node', 'execution_time_ms', 'explored_nodes', 'space_query_byte']
        cols_ch = ['start_node', 'end_node', 'execution_time_ms', 'explored_nodes', 'space_query_byte', 'preprocessing_time_ms']
        df_dijkstra = df_dijkstra[cols_dijkstra]
        df_ch = df_ch[cols_ch]

        # --- Unione dei DataFrame ---
        df_comparison = pd.merge(
            df_dijkstra,
            df_ch,
            on=['start_node', 'end_node'],
            suffixes=('_dijkstra', '_ch')
        )
        
        df_comparison.sort_values(by='execution_time_ms_dijkstra', inplace=True)
        
        # --- Creazione dei Grafici (come nello step precedente) ---
        num_queries = len(df_comparison)
        query_indices = np.arange(num_queries)
        bar_width = 0.35

        # 1. Grafico: Tempo di Esecuzione
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.bar(query_indices - bar_width/2, df_comparison['execution_time_ms_dijkstra'], bar_width, label='Dijkstra', color='skyblue')
        ax.bar(query_indices + bar_width/2, df_comparison['execution_time_ms_ch'], bar_width, label='Contraction Hierarchies', color='salmon')
        ax.set_yscale('log')
        ax.set_xlabel('Singola Query (ordinata per tempo di Dijkstra)')
        ax.set_ylabel('Tempo di Esecuzione (ms) - Scala Logaritmica')
        ax.set_title('Confronto Tempo di Esecuzione: Dijkstra vs. CH')
        ax.legend()
        plt.tight_layout()
        plt.savefig('execution_time_comparison.png')
        print("Grafico 'execution_time_comparison.png' generato.")

        # 2. Grafico: Nodi Esplorati
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.bar(query_indices - bar_width/2, df_comparison['explored_nodes_dijkstra'], bar_width, label='Dijkstra', color='skyblue')
        ax.bar(query_indices + bar_width/2, df_comparison['explored_nodes_ch'], bar_width, label='Contraction Hierarchies', color='salmon')
        ax.set_yscale('log')
        ax.set_xlabel('Singola Query')
        ax.set_ylabel('Nodi Esplorati - Scala Logaritmica')
        ax.set_title('Confronto Nodi Esplorati: Dijkstra vs. CH')
        ax.legend()
        plt.tight_layout()
        plt.savefig('explored_nodes_comparison.png')
        print("Grafico 'explored_nodes_comparison.png' generato.")
        
        # 3. Grafico: Occupazione di Memoria
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.bar(query_indices - bar_width/2, df_comparison['space_query_byte_dijkstra'], bar_width, label='Dijkstra', color='skyblue')
        ax.bar(query_indices + bar_width/2, df_comparison['space_query_byte_ch'], bar_width, label='Contraction Hierarchies', color='salmon')
        ax.set_xlabel('Singola Query')
        ax.set_ylabel('Occupazione Memoria per Query (Byte)')
        ax.set_title('Confronto Occupazione Memoria: Dijkstra vs. CH')
        ax.legend()
        plt.tight_layout()
        plt.savefig('space_occupation_comparison.png')
        print("Grafico 'space_occupation_comparison.png' generato.")

        # --- Calcolo del Confronto Temporale Totale ---
        # Somma di tutti i tempi di esecuzione di Dijkstra
        total_dijkstra_time = df_comparison['execution_time_ms_dijkstra'].sum()

        # Tempo di pre-elaborazione di CH (è lo stesso per tutte le righe)
        ch_preprocessing_time = df_comparison['preprocessing_time_ms'].iloc[0]
        
        # Somma di tutti i tempi di esecuzione delle query CH
        total_ch_query_time = df_comparison['execution_time_ms_ch'].sum()
        
        # Tempo totale per CH = pre-elaborazione + somma delle query
        total_ch_time = ch_preprocessing_time + total_ch_query_time

        print("\n--- Analisi del Tempo Totale ---")
        print(f"Numero di query eseguite: {num_queries}")
        print(f"Tempo totale di Dijkstra (somma delle query): {total_dijkstra_time / 1000:.2f} secondi")
        print("-" * 30)
        print(f"Tempo di pre-elaborazione CH: {ch_preprocessing_time / 1000:.2f} secondi")
        print(f"Tempo totale delle query CH: {total_ch_query_time / 1000:.2f} secondi")
        print(f"Tempo totale complessivo CH (Prep. + Query): {total_ch_time / 1000:.2f} secondi")
        print("-" * 30)

        if total_ch_time > total_dijkstra_time:
            print("RISULTATO: Il tempo totale di CH (incluso preprocessing) è MAGGIORE del tempo totale di Dijkstra.")
        else:
            print("RISULTATO: Il tempo totale di CH (incluso preprocessing) è MINORE del tempo totale di Dijkstra.")
            
        # Calcolo del punto di pareggio (break-even point)
        avg_dijkstra_time = df_comparison['execution_time_ms_dijkstra'].mean()
        avg_ch_time = df_comparison['execution_time_ms_ch'].mean()
        if avg_dijkstra_time > avg_ch_time:
            break_even_queries = ch_preprocessing_time / (avg_dijkstra_time - avg_ch_time)
            print(f"\nCH diventa più conveniente di Dijkstra dopo circa {int(break_even_queries)} query.")

