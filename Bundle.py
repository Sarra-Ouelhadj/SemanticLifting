import geopandas as gpd
from abc import ABC, abstractmethod
import pandas as pd
import requests
from library import helpers as h

class Bundle(ABC) :
 
    name : str
    IRI : str
    definition : str
    linked_to : list
    
    dataset: gpd.GeoDataFrame
     
    instances_namespace = "https://data.grandlyon.com/id/"
    ontology_namespace = "https://data.grandlyon.com/onto/"
    vocabulary_namespace ="https://data.grandlyon.com/vocab/"

    def __init__(self, name : str, dataset : gpd.GeoDataFrame, IRI = None, definition = None, linked_to = []) -> None:
        self.name = h.convertToPascalcase(name)
        self.dataset=dataset
        self.IRI = IRI
        self.definition = definition
        self.linked_to = linked_to
    
    def show(self):
        print ("name :" , self.name)
        print ("IRI :" ,self.IRI)
        print ("definition :" ,self.definition)
    
    def next(self) :
        next = {}
        for bun in self.linked_to:
            next[bun["name"]] = bun["destination"]
        return next
    
    @abstractmethod
    def document(self):
        pass

    @abstractmethod
    def annotate(self):
        pass

    @abstractmethod
    def validate(self, errors = [], narrow = True):
        pass
    
    @abstractmethod
    def generateOntology(self, narrow = True, kpi_results = pd.DataFrame()):
        pass

    def insert(instance_path:str="./results/instances.ttl"):
        
        headers = {
            'Content-Type': 'application/x-turtle',
            'Accept': 'application/json'
        }

        with open(instance_path, 'rb') as f:
            requests.post('http://192.168.123.158:7200/repositories/Project/statements', data=f, headers=headers)

    
    #---------------------------------- dataset utilities --------------------------------
    def show_dataset(self):
        print(self.dataset)

    #---------------------------------- utilities --------------------------------
    
    def index(self, lst:list, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        raise Exception
    
    def add_link(self, name: str, destination: "Bundle", IRI=None, definition : str=None):
        association_element={}
        association_element["name"]=name
        association_element["IRI"]=IRI
        association_element["definition"]=definition
        association_element["source"] = self
        association_element["destination"] = destination
        
        self.linked_to.append(association_element)

    def get_link(self, name:str = None, source:str = None, destination:str = None) -> dict:
        args = locals()
        if (any(args.values())==True) :
            for association_element in self.linked_to:
                if (args['source']!= None):
                    if (association_element['source'].name == h.convertToPascalcase(source)): return association_element
                    
                else :
                    if (args['destination']!= None):
                        if (association_element['destination'].name == h.convertToPascalcase(destination)): return association_element
                    else :
                        if (association_element['name'] == name) : return association_element
            raise Exception("L'association indiquée n'existe pas")
        else:
            raise ValueError('Au moins un paramètre par défaut doit être passé !')

    def write_json(self):
        ...
