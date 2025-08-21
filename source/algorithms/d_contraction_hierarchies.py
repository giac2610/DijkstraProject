import time
import sys

from utils.utils import RawData

class Contraction_Hierarchies:
     def __init__(self):
          self.graph = None
          self.num_queries = 0
          self.results = []
          self.dataUtils = RawData()
     
     def run(self, graph, num_queries, start_node_list, end_node_list):
          pass

     def _create_contraction_hierarchy(self):
          pass

     def _ch_algotithm(self):
          pass

     def _save_results_to_csv(self):
          self.dataUtils.save_to_csv('ch_results.csv',self.results)