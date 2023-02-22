import copy
import subprocess
from Bundle import Bundle
from BundleCollection import BundleCollection
from SemanticModel import SemanticModel
import json
from library.initiateSemanticModelFromJsonSchema import *
from library import helpers as h
from rdflib.namespace import RDF, RDFS, OWL, SKOS
from rdflib import Graph, Literal, URIRef, Namespace

class BundleEnum(Bundle):
    
    def annotate(self, enumerations:dict=None, enum_values:dict=None):
        """
        >>> annotate(enum_values={("reseau_loc","REV"):"http://exemple/REV"})
        """
        args = locals()
        if (any(args.values())==True):
            
            if (enumerations!=None):
                enumerations_keys=list(enumerations.keys())
                for value in enumerations_keys:
                    i=self.semantic_model.index(self.semantic_model.enumerations,'name', value)
                    #affecter l'IRI
                    self.semantic_model.enumerations[i]['IRI']=enumerations[value]      

            if (enum_values!=None):
                enum_values_keys=list(enum_values.keys())
                for value_x, value_y in enum_values_keys:
                    i=self.semantic_model.index(self.semantic_model.enumerations,'name', value_x)
                    j=self.semantic_model.index(self.semantic_model.enumerations[i]['values'],'name', value_y)
                    #affecter l'IRI
                    self.semantic_model.enumerations[i]['values'][j]['IRI']=enum_values[(value_x, value_y)]
        else:
            raise ValueError('Au moins un paramètre par défaut doit être passé !')

    def validate(self):
        
        """
        enumerations validation \n
        0. Chaque énumération doit avoir un nom
        1. Chaque énumération doit avoir un lien de référence ou une définition
        2. Chaque énumération doit avoir une source

        enumeration values validation \n
        0. Chaque valeur d'énumération doit avoir un nom
        1. Chaque valeur d'énumération doit avoir un lien de référence ou une définition

        """
        self.validate_association()
        errors = []
        #------------------------
        #enumerations validation
        #------------------------

        for enum in self.semantic_model.enumerations :
            #0. Chaque énumération doit avoir un nom
            if (enum['name']=='' or enum['name']== None) : errors.append ("Le nom de l'énumération est obligatoire")

            #1. Chaque énumération doit avoir un lien de référence ou une définition
            if ((enum['IRI']=='' or enum['IRI']== None) and (enum['definition']=='' or enum['definition'] == None )): errors.append (f"L'énumération {enum['name']} doit avoir un lien de référence ou une définition")

            #2. Chaque énumération doit avoir une source
            if (enum['source']=='' or enum['source']==None): errors.append (f"L'énumération {enum['name']} n'a pas de source")        
        
        #------------------------
        #enumeration values validation
        #------------------------
            for enum_val in enum['values']:
                #0. Chaque valeur d'énumération doit avoir un nom
                if (enum_val['name']=='' or enum_val['name']== None) : errors.append (f"Le nom de la valeur d'énumération {enum['name']} est obligatoire")

                #1. Chaque valeur d'énumération doit avoir un lien de référence ou une définition
                if ((enum_val['IRI']=='' or enum_val['IRI']== None) and (enum_val['definition']=='' or enum_val['definition'] == None )): errors.append (f"La valeur d'énumération {enum_val['name']} doit avoir un lien de référence ou une définition")

        if errors:
            raise Exception (errors)
        else : return True
    
    def generateOntology(self,vocabulary_path:str):
        """generate ontology files from the semantic model"""

        VS = Namespace("http://www.w3.org/2003/06/sw-vocab-status/ns#")
        g2 = Graph ()

        #------------------------
        #Individuals
        #------------------------
        for enum in self.semantic_model.enumerations:
            if enum["IRI"]!="":
                enumerationURI = URIRef(enum["IRI"])
            else :
                enumerationURI = URIRef(self.semantic_model.vocabulary_namespace + h.convertToPascalcase(enum["name"]))

                self.annotate(enumerations={enum["name"]:str(enumerationURI)})

                g2.add((enumerationURI, RDF.type, SKOS.ConceptScheme))
                g2.add((enumerationURI,SKOS.prefLabel, Literal(enum["name"])))
                g2.add((enumerationURI,SKOS.definition, Literal(enum["definition"])))
                g2.add((enumerationURI,RDFS.isDefinedBy, URIRef(self.semantic_model.vocabulary_namespace)))
                g2.add((enumerationURI,VS.term_status, Literal("testing")))
                
            for val in filter(lambda value: False if value["IRI"]!="" else True, enum["values"]):     
                valueURI = URIRef(self.semantic_model.vocabulary_namespace + h.convertToSnakecase(val["name"]))

                self.annotate(enum_values={(enum["name"],val["name"]):str(valueURI)})

                g2.add((valueURI,RDF.type, SKOS.Concept))    
                g2.add((valueURI,SKOS.prefLabel, Literal(val["name"])))
                g2.add((valueURI,SKOS.definition, Literal(val["definition"])))
                g2.add((valueURI,RDFS.isDefinedBy, URIRef(self.semantic_model.vocabulary_namespace)))
                g2.add((valueURI,SKOS.inScheme, enumerationURI))
                g2.add((valueURI,VS.term_status, Literal("testing")))

        with open(vocabulary_path, 'w') as fv :
            fv.write(g2.serialize(format="turtle"))
