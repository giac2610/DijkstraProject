import csv
import sys
import pandas as pd
import os

class RawData:
    def get_deep_size(self, obj, seen=None):
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)
        size = sys.getsizeof(obj)
        if isinstance(obj, dict):
            size += sum(self.get_deep_size(v, seen) for v in obj.values())
            size += sum(self.get_deep_size(k, seen) for k in obj.keys())
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum(self.get_deep_size(i, seen) for i in obj)
        return size

    def save_to_csv(self, filename, data):
        """
        Salva una lista di dizionari in un file CSV all'interno della cartella 'results'.
        """
        print(f"\n--- Diagnostica di Salvataggio per '{filename}' ---")
        if not data:
            print("RISULTATO: La lista dei dati è VUOTA. Nessun file verrà salvato.")
            return
        
        print(f"RISULTATO: Ricevuti {len(data)} record da salvare.")
        print(f"  - Colonne trovate: {list(data[0].keys())}")
        
        results_dir = 'results'
        os.makedirs(results_dir, exist_ok=True)
        
        filepath = os.path.join(results_dir, filename)
        
        keys = data[0].keys()
        try:
            with open(filepath, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(data)
            print(f"Dati salvati con successo in {filepath}.")
        except Exception as e:
            print(f"!!! ERRORE CRITICO DURANTE LA SCRITTURA του FILE: {e} !!!")

    def load_dijkstra_results(self, filename='dijkstra_results.csv'):
        filepath = os.path.join('results', filename)
        return pd.read_csv(filepath)

    def load_ch_results(self, filename='contraction_hierarchies_results.csv'):
        filepath = os.path.join('results', filename)
        return pd.read_csv(filepath)