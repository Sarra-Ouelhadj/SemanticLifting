import copy
import subprocess
from Bundle import Bundle
from BundleCollection import BundleCollection
import json
from library import helpers as h
from rdflib.namespace import RDF, RDFS, OWL, SKOS
from rdflib import Graph, Literal, URIRef, Namespace
import geopandas as gpd
import pandas as pd

class BundleEnum(Bundle):

    values = []
    source : str = ""
    type : str = ""
    required : str = ""

    def __init__(self, name: str, dataset: gpd.GeoDataFrame, IRI=None, definition=None, linked_to=[]) -> None:
        super().__init__(name, dataset, IRI, definition, linked_to)
        self.values = []
        self.source = None
        self.type = None
        self.required = None
    
    def show(self):
        print("------- Enumeration -------")
        super().show()
        print("source :" ,self.source)
        print("type :" ,self.type)
        print("required :" ,self.required)
        print("\t ------- Values -------")
        for e in self.values:
            print("\t name :" ,e["name"])
            print("\t definition :" ,e["definition"])
            print("\t IRI :" ,e["IRI"])
            print("\t --------------")

    def annotate(self, enumeration_IRI:str=None, enum_values:dict=None):
        """
        >>> annotate(enumeration_IRI="http://schema.org/Thing")
        >>> annotate(enum_values={"REV":"http://exemple/REV"})
        """
        args = locals()
        if (any(args.values())==True):
            
            if (enumeration_IRI!=None):
                self.IRI = enumeration_IRI      

            if (enum_values!=None):
                enum_keys=list(enum_values.keys())
                for value in enum_keys:
                    i=self.index(self.values,'name', value)
                    #affecter l'IRI
                    self.values[i]['IRI']=enum_values[value]
        else:
            raise ValueError('Au moins un paramètre par défaut doit être passé !')

    def validate(self, errors = [], narrow = True):
        
        """
        enumerations validation \n
        0. Chaque énumération doit avoir un nom
        1. Chaque énumération doit avoir un lien de référence ou une définition
        2. Chaque énumération doit avoir une source

        enumeration values validation \n
        0. Chaque valeur d'énumération doit avoir un nom
        1. Chaque valeur d'énumération doit avoir un lien de référence ou une définition

        """
        errors = errors
        #------------------------
        #enumeration validation
        #------------------------

        #0. L'énumération doit avoir un nom
        if (self.name =='' or self.name == None) : errors.append ("Le nom de l'énumération est obligatoire")

        #1. L'énumération doit avoir un lien de référence ou une définition
        if ((self.IRI == '' or self.IRI == None) and (self.definition =='' or self.definition == None )): errors.append (f"L'énumération {self.name} doit avoir un lien de référence ou une définition")

        #2. L'énumération doit avoir une source
        if (self.source == '' or self.source == None): errors.append (f"L'énumération {self.name} n'a pas de source")        
        
        #------------------------
        #enumeration values validation
        #------------------------
        for enum_val in self.values:
            #0. Chaque valeur d'énumération doit avoir un nom
            if (enum_val['name']=='' or enum_val['name']== None) : errors.append (f"Le nom de la valeur d'énumération {self.name} est obligatoire")

            #1. Chaque valeur d'énumération doit avoir un lien de référence ou une définition
            if ((enum_val['IRI']=='' or enum_val['IRI']== None) and (enum_val['definition']=='' or enum_val['definition'] == None )): errors.append (f"La valeur d'énumération {enum_val['name']} doit avoir un lien de référence ou une définition")

        try :
            if (errors):
                raise Exception (errors)
            else : return True
        except Exception as e :
            raise e

    def document(self, enum_definition : str = None, enum_values:dict = None):

        args = locals()
        if (any(args.values())==True):
            if (enum_definition != None):
                self.definition = enum_definition
        
            if (enum_values != None) :
                enum_keys = list(enum_values.keys())
                for value in enum_keys:
                    i=self.index(self.values, 'name', value)
                    # donner une définition
                    self.values[i]['definition']= enum_values[value]
        else:
            raise ValueError('Au moins un paramètre par défaut doit être passé !')

    def generateOntology(self,vocabulary_path:str, narrow = True, vocabulary_graph=Graph(), kpi_results = pd.DataFrame()):
        """generate ontology files from the semantic model"""

        VS = Namespace("http://www.w3.org/2003/06/sw-vocab-status/ns#")
        g2 = vocabulary_graph

        enum_created = False
        value_created = False
        
        #------------------------
        #Individuals
        #------------------------
        if (self.IRI != None and self.IRI != "") :
            enumerationURI = URIRef(self.IRI)
        else :
            enumerationURI = URIRef(self.vocabulary_namespace + h.convertToPascalcase(self.name))

            self.annotate(enumeration_IRI=str(enumerationURI))

            g2.add((enumerationURI, RDF.type, SKOS.ConceptScheme))
            g2.add((enumerationURI,SKOS.prefLabel, Literal(self.name)))
            g2.add((enumerationURI,SKOS.definition, Literal(self.definition)))
            g2.add((enumerationURI,RDFS.isDefinedBy, URIRef(self.vocabulary_namespace)))
            g2.add((enumerationURI,VS.term_status, Literal("testing")))
            enum_created = True

            if (narrow == False) :
                df = pd.DataFrame({
                    "IRI" : str(enumerationURI),
                    "type": pd.Categorical(["ConceptScheme"]),
                    "related": "NA"
                })
                
                kpi_results = pd.concat([kpi_results,df],ignore_index=True)
            
        for val in filter(lambda value: False if (value["IRI"]!="" and value["IRI"]!=None) else True, self.values):     
            valueURI = URIRef(self.vocabulary_namespace + h.convertToSnakecase(val["name"]))

            self.annotate(enum_values={val["name"]:str(valueURI)})

            g2.add((valueURI,RDF.type, SKOS.Concept))    
            g2.add((valueURI,SKOS.prefLabel, Literal(val["name"])))
            g2.add((valueURI,SKOS.definition, Literal(val["definition"])))
            g2.add((valueURI,RDFS.isDefinedBy, URIRef(self.vocabulary_namespace)))
            g2.add((valueURI,SKOS.inScheme, enumerationURI))
            g2.add((valueURI,VS.term_status, Literal("testing")))
            value_created = True

            df = pd.DataFrame({
                "IRI" : str(valueURI),
                "type": pd.Categorical(["Concept"]),
                "related": self.name
            })
            
            kpi_results = pd.concat([kpi_results,df],ignore_index=True)

        if (narrow and enum_created):
            print(f"IRI de l'énumération {self.name} a été créé : {self.IRI}")
            
        if (narrow and value_created):
            
            print(f"Le nombre de valeurs créées pour l'énumération `{self.name}` est : {kpi_results.loc[kpi_results['type']=='Concept', 'IRI'].count()}")

        with open(vocabulary_path, 'a') as fv :
            fv.write(g2.serialize(format="turtle"))

        if (narrow == False) : return g2, kpi_results