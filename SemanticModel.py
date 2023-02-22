from abc import abstractmethod
import json
from library.initiateSemanticModelFromJsonSchema import *

class SemanticModel() :
    
    classes:list
    associations:list
    enumerations:list

    ontology_namespace = "https://data.grandlyon.com/onto/"
    vocabulary_namespace ="https://data.grandlyon.com/vocab/"

    def __init__(self, d:dict) -> None:
        self.classes = d['classes']
        self.associations = d['associations']
        self.enumerations = d['enumerations']

    def show_all(self) -> dict:
        d={}
        d['classes']=self.classes
        d['associations']=self.associations
        d['enumerations']=self.enumerations
        print(d)

    def initiate_from_jsonSchema(schema_url: str, title:str):
        d=initiateSemanticModelFromJsonSchema(schema_url, title)
        return SemanticModel(d)

    def write_json(self,path:str):
        with open(path, 'w') as f:
            d={}
            d['classes']=self.classes
            d['associations']=self.associations
            d['enumerations']=self.enumerations
            json.dump(d,f, ensure_ascii=False)
    #TODO
    def write_excel():
        ...
    
    @abstractmethod
    def annotate(self, class_:dict=None, attributes:dict=None, enumerations:dict=None, enum_values:dict=None, associations:dict=None):
        pass

    @abstractmethod
    def validate(self):
        pass
    
    @abstractmethod
    def generateOntology(self, ontology_path:str, vocabulary_path:str):
        pass
    
    #---------------------------------- utilities --------------------------------
    
    def index(self, lst:list, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        raise Exception

    def get_id(self) -> dict:
        for attribute_element in self.classes[0]['attributes']:
            if attribute_element['id']=="oui":
                return attribute_element
        raise Exception ("L'identifiant de la classe n'est pas précisé dans le modèle sémantique")
    
    def get_attribute(self, name_attribute: str) -> dict:
        for attribute_element in self.classes[0]["attributes"]:
            if attribute_element["name"]==name_attribute :
                return attribute_element
        raise Exception("L'attribut indiqué n'existe pas")

    def get_enumeration(self, name_enumeration: str) -> dict:
        for enumeration_element in self.enumerations:
            if enumeration_element["name"] == name_enumeration :
                return enumeration_element
        raise Exception("L'énumération indiquée n'existe pas")
    
    def get_association(self, name_association:str = None, source:str = None, destination:str=None) -> dict:
        args = locals()
        if (any(args.values())==True) :
            for association_element in self.associations:
                if (args['source']!= None):
                    if (association_element['source'] == source): return association_element
                else :
                    if (args['destination']!= None):
                        if (association_element['destination'] == destination): return association_element
                    else :
                        if (association_element['name'] == name_association) : return association_element
            raise Exception("L'association indiquée n'existe pas")
        else:
            raise ValueError('Au moins un paramètre par défaut doit être passé !')
        
    def add_class(self, name: str, IRI: str="", definition : str="", attributes:list=[]):
        class_element={}
        class_element["name"]=name
        class_element["IRI"]=IRI
        class_element["definition"]=definition
        class_element["attributes"] = attributes
        
        self.classes.append(class_element)
        return self

    def add_association(self, name: str, source:str, destination:str, IRI: str="", definition : str=""):
        association_element={}
        association_element["name"]=name
        association_element["IRI"]=IRI
        association_element["definition"]=definition
        association_element["source"] = source
        association_element["destination"] = destination
        
        self.associations.append(association_element)
        return self
    
    def isAtomic(self) -> bool:
        """
        Si le modèle sémantique contient une seule classe ou (exclusif) une seule énumération UML.
        Les associations ne sont pas incluses dans la définition de l'atomicité du modèle sémantique
        """
        return False if (len(self.classes)>1 or len(self.enumerations)>1 or (len(self.classes)>=1 and len(self.enumerations)>=1)) else True 