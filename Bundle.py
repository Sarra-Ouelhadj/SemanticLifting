from SemanticModel import SemanticModel
import geopandas as gpd
from abc import ABC, abstractmethod

class Bundle(ABC) :
    
    semantic_model : SemanticModel
    dataset: gpd.GeoDataFrame
     
    instances_namespace = "https://data.grandlyon.com/id/"

    def __init__(self, semantic_model : SemanticModel, dataset : gpd.GeoDataFrame) -> None:
        self.semantic_model=semantic_model
        self.dataset=dataset

    def annotate_association(self, associations:dict):
        """
        >>> annotate_association(associations={"reseau_loc":"http://exemple/reseau_loc"})
        """
        associations_keys=list(associations.keys())
        for value in associations_keys: 
            i=self.semantic_model.index(self.semantic_model.associations,'name', value)
            #affecter l'IRI
            self.semantic_model.associations[i]['IRI']=associations[value]

    def validate_association(self):
        """
        associations validation \n
        0. Chaque association doit avoir un nom
        1. Chaque association doit avoir un lien de référence ou une définition
        2. Chaque association doit avoir une source
        3. Chaque association doit avoir une destination
        """
        errors =[]
        #------------------------
        #associations validation
        #------------------------

        for ass in self.semantic_model.associations :
            #0. Chaque association doit avoir un nom
            if (ass['name']=='' or ass['name']== None): errors.append ("Le nom de l'association est obligatoire")

            #1. Chaque association doit avoir un lien de référence ou une définition
            if ((ass['IRI']=='' or ass['IRI']== None) and (ass['definition']=='' or ass['definition'] == None )): errors.append(f"L'association {ass['name']} doit avoir un lien de référence ou une définition")

            #2. Chaque association doit avoir une source
            if (ass['source']=='' or ass['source']==None) : errors.append (f"L'association {ass['name']} doit avoir une source")

            #3. Chaque association doit avoir une destination
            if (ass['destination']=='' or ass['destination']==None) : errors.append (f"L'association {ass['name']} doit avoir une destination")
            
        if errors:
            raise Exception (errors)
        else : return True

    
    #---------------------------------- dataset utilities --------------------------------
    def show_dataset(self):
        print(self.dataset)
