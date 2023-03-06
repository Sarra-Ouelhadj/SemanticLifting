import networkx as nx
from matplotlib import pyplot as plt

class BundleCollection :

    @classmethod
    def __init__(cls,root):
        cls.root = root
        cls.graph = nx.DiGraph()
        cls.graph.add_node(root)
        for l in root.linked_to :
            cls.graph.add_edge(root, l["destination"], predicate = l["name"], operation = "creation")
    
    @classmethod
    def add_bundle(cls, origin_bundle, new_bundle, predicate:str, operation:str = "split"):
        cls.graph.add_edge(origin_bundle, new_bundle, predicate = predicate, operation = operation)

    @classmethod
    def metadata_info(cls):
        nb_bun = cls.graph.number_of_nodes()
        print("Nombre de bundles créés : ", nb_bun)
        nb_cl = 0
        for n in cls.graph:
            if (str(type(n)) == "<class 'BundleClass.BundleClass'>") :
                nb_cl+=1
        print("Nombre de bundles de type `classe` : ", nb_cl)
        print("Nombre de bundles de type `énumération` : ", nb_bun - nb_cl)
        return(nb_bun, nb_cl, nb_bun - nb_cl)

    @classmethod
    def show(cls):
        labeldict = {}
        edgedict = {}
        colors = []
        for n in cls.graph:
            labeldict[n]= n.name
            if (str(type(n)) == "<class 'BundleClass.BundleClass'>") :
                colors.append("orange")
            else : 
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
    