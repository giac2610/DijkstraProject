from abc import ABC, abstractmethod

class GraphInterface(ABC):
     
     def __init__(self):
          pass
     
     @abstractmethod
     def _generate(self):
          pass
     
     @abstractmethod
     def get_random_node(self, start_node=None):
          pass

     @abstractmethod
     def plot_graph(self):
          pass