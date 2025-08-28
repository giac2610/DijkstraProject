import sys
import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import csv

class RawData:
    def __init__(self):
        pass

    def save_to_csv(self, filename, data):
        if not data:
            print(f"Warning: No data to save to {filename}")
            return
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved to {filename}")
    
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
    
    def plot_and_analyze(self, df_dijkstra, df_ch):
        
        # --- Nomi Colonne DIJKSTRA ---
        df_dijkstra.rename(columns={
            'preproccessing_time (ms)': 'preprocessing_time_ms', # Corretto typo
            'execution_time (ms)': 'execution_time_ms',
            'explored_nodes': 'explored_nodes',
            'space_occupation (Byte):': 'space_occupation_byte' # Con i due punti
        }, inplace=True)

        # --- Nomi Colonne CONTRACTION HIERARCHIES ---
        df_ch.rename(columns={
            'preprocessing_time (ms)': 'preprocessing_time_ms',
            'execution_time (ms)': 'execution_time_ms',
            'explored_nodes': 'explored_nodes',
            'space_occupation (Byte)': 'space_occupation_byte', # Senza due punti
            'space_preprocessing (Byte)': 'space_preprocessing_byte',
            'space_query (Byte)': 'space_query_byte'
        }, inplace=True)
        
        # --- Selezione Colonne Rilevanti ---
        cols_dijkstra = ['start_node', 'end_node', 'preprocessing_time_ms', 'execution_time_ms', 'explored_nodes', 'space_occupation_byte']
        cols_ch = ['start_node', 'end_node', 'preprocessing_time_ms', 'execution_time_ms', 'explored_nodes', 'space_occupation_byte', 'space_preprocessing_byte', 'space_query_byte']
        
        df_dijkstra = df_dijkstra[cols_dijkstra]
        df_ch = df_ch[cols_ch]

        df_comparison = pd.merge(
            df_dijkstra,
            df_ch,
            on=['start_node', 'end_node'],
            suffixes=('_dijkstra', '_ch')
        )
        
        if df_comparison.empty:
            print("Warning: No matching queries found between Dijkstra and CH results. Cannot generate plots.")
            return
            
        df_comparison.sort_values(by='execution_time_ms_dijkstra', inplace=True)
        
        # --- Creazione dei Grafici ---
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
        

        fig, ax = plt.subplots(figsize=(12, 7))
        ax.bar(query_indices - bar_width/2, df_comparison['space_occupation_byte_dijkstra'], bar_width, label='Dijkstra', color='skyblue')
        ax.bar(query_indices + bar_width/2, df_comparison['space_occupation_byte_ch'], bar_width, label='Contraction Hierarchies', color='salmon')
        ax.set_xlabel('Singola Query')
        ax.set_ylabel('Occupazione Memoria Totale per Query (Byte)')
        ax.set_title('Confronto Occupazione Memoria: Dijkstra vs. CH')
        ax.legend()
        plt.tight_layout()
        plt.savefig('space_occupation_comparison.png')
        print("Grafico 'space_occupation_comparison.png' generato.")

        # --- Calcolo del Confronto Temporale Totale ---
        total_dijkstra_time = df_comparison['execution_time_ms_dijkstra'].sum()
        ch_preprocessing_time = df_comparison['preprocessing_time_ms_ch'].iloc[0]
        total_ch_query_time = df_comparison['execution_time_ms_ch'].sum()
        total_ch_time = ch_preprocessing_time + total_ch_query_time

        print("\n--- Analisi del Tempo Totale ---")
        print(f"Numero di query eseguite: {num_queries}")
        print(f"Tempo totale di Dijkstra (somma delle query): {total_dijkstra_time / 1000:.2f} secondi")
        print("-" * 30)
        if ch_preprocessing_time/1000 <60:
            print(f"Tempo di pre-elaborazione CH: {ch_preprocessing_time / 1000:.2f} secondi")
        else:
            print(f"Tempo di pre-elaborazione CH: {ch_preprocessing_time / 60000:.2f} minuti")
        print(f"Tempo totale delle query CH: {total_ch_query_time / 1000:.2f} secondi")
        print(f"Tempo totale complessivo CH (Prep. + Query): {total_ch_time / 1000:.2f} secondi")
        print("-" * 30)

        if total_ch_time > total_dijkstra_time:
            print("RISULTATO: Il tempo totale di CH (incluso preprocessing) è MAGGIORE del tempo totale di Dijkstra.")
        else:
            print("RISULTATO: Il tempo totale di CH (incluso preprocessing) è MINORE del tempo totale di Dijkstra.")
            
        avg_dijkstra_time = df_comparison['execution_time_ms_dijkstra'].mean()
        avg_ch_time = df_comparison['execution_time_ms_ch'].mean()
        if avg_dijkstra_time > avg_ch_time:
            time_diff = avg_dijkstra_time - avg_ch_time
            if time_diff > 0:
                break_even_queries = ch_preprocessing_time / time_diff
                print(f"\nCH diventa più conveniente di Dijkstra dopo circa {int(break_even_queries)} query.")