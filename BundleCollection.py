import networkx as nx
from matplotlib import pyplot as plt

class BundleCollection :

    @classmethod
    def __init__(cls,root):
        cls.graph = nx.DiGraph()
        cls.graph.add_node(root)
    
    @classmethod
    def add_bundle(cls, origin_bundle, new_bundle, predicate:str, operation:str = "split"):
        cls.graph.add_edge(origin_bundle, new_bundle, predicate = predicate, operation = operation)

    @classmethod
    def list_bundles(cls):
        l = []
        for n in cls.graph:
            l.append(n)
        return l

    @classmethod
    def get_neighbour(cls, node, predicate : str):
        for nbr, datadict in cls.graph.adj[node].items():
            if datadict['predicate'] == predicate :
                return nbr
        return Exception

    @classmethod
    def show(cls):
        labeldict = {}
        edgedict = {}
        colors = []
        for n in cls.graph:
            if (str(type(n)) == "<class 'BundleClass.BundleClass'>") :
                labeldict[n]=n.semantic_model.classes[0]['name']
                colors.append("orange")
            else : 
                labeldict[n]=n.semantic_model.enumerations[0]['name']
                colors.append("cyan")
        for u, v, d in cls.graph.edges(data='predicate'):
            edgedict[u,v] = d
        pos = nx.spring_layout(cls.graph)
        nx.draw(cls.graph, pos, labels = labeldict ,with_labels=True, node_color = colors)
        nx.draw_networkx_edge_labels(cls.graph, pos, edge_labels = edgedict)
        plt.show()

    @classmethod
    def save_figure(cls, path, format):
        plt.savefig(path, format=format)
        plt.clf()
