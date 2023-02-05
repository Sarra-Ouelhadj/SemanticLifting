import json
from library.initiateSemanticModelFromJsonSchema import *

class SemanticModel :
    
    classes:list
    associations:list
    enumerations:list

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
    
    def annotate(self, class_:dict=None, attributes:dict=None, enumerations:dict=None, enum_values:dict=None, associations:dict=None):
        """
        >>> annotate(class_={"AmenagementCyclable":"http://schema.org/Thing"})
        >>> annotate(attributes={"nom_loc":"http://schema.org/name", "num_iti":"http://schema.org/name"})
        >>> annotate(associations={"aPourreseau_loc":"http://exemple/aPourreseau_loc"})
        >>> annotate(enum_values={("reseau_loc_options","REV"):"http://exemple/REV"})
        """
        args = locals()
        if (any(args.values())==True):
            if (class_!=None):
                self.classes[0]['IRI']=class_[self.classes[0]['name']]

            if (attributes!=None):
                attributes_keys = list(attributes.keys())
                for value in attributes_keys: 
                    i=self.index(self.classes[0]['attributes'],'name', value)
                    #affecter l'IRI
                    self.classes[0]['attributes'][i]['IRI']=attributes[value]

            if (associations!=None):
                associations_keys=list(associations.keys())
                for value in associations_keys: 
                    i=self.index(self.associations,'name', value)
                    #affecter l'IRI
                    self.associations[i]['IRI']=associations[value]
            
            if (enumerations!=None):
                enumerations_keys=list(enumerations.keys())
                for value in enumerations_keys:
                    i=self.index(self.enumerations,'name', value)
                    #affecter l'IRI
                    self.enumerations[i]['IRI']=enumerations[value]      

            if (enum_values!=None):
                enum_values_keys=list(enum_values.keys())
                for value_x, value_y in enum_values_keys:
                    i=self.index(self.enumerations,'name', value_x)
                    j=self.index(self.enumerations[i]['values'],'name', value_y)
                    #affecter l'IRI
                    self.enumerations[i]['values'][j]['IRI']=enum_values[(value_x, value_y)]
        else:
            raise ValueError('At least one default parameter should be passed!')

    def index(self, lst:list, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        raise Exception

    #----------------------------------Brainstoming---------------------------------------------
    def isAtomic(self) -> bool:
        """si le modèle sémantique contient un seul élément UML"""
        return False if (len(self.classes)>1 or len(self.enumerations)>1 or len(self.associations)>1) else True 
    
    def get_class(self, name: str) -> dict :
        for class_element in self.classes:
            if class_element["name"]==name :
                return class_element
        else : raise Exception("La classe indiquée n'existe pas")
    
    def add_class(self, name: str, IRI: str = None, definition : str = None) -> None:
        class_element={}
        class_element["name"]=name
        class_element["IRI"]=IRI
        class_element["definition"]=definition
        class_element["attributes"] = []

        #ajouter un attribut exemple pour la nouvelle classe
        self.add_attribute_class(class_element,name_attribute="attribut1")
        
        self.classes.append(class_element)
        return self

    def delete_class(self, name : str) -> None:
        cl = self.get_class(name)
        self.classes.remove(cl)
        return self

    def get_attribute_class(self, name_class:str, name_attribute: str) -> 'tuple[dict, dict]':
        class_element= self.get_class(name_class)
        for attribute_element in class_element["attributes"]:
            if attribute_element["name"]==name_attribute :
                return class_element, attribute_element
        else : raise Exception("L'attribut indiqué n'existe pas")
    
    def add_attribute_class(self, class_element:dict, name_attribute: str, IRI:str=None, source:str=None, definition:str=None, type:str="string", required:bool="non", id:bool="non") -> None:
        element_niv1={}
        element_niv1["name"]=name_attribute
        element_niv1["IRI"]=IRI
        element_niv1["source"]=source
        element_niv1["definition"]=definition
        element_niv1["type"]=type
        element_niv1["required"]=required
        element_niv1["id"]=id
        
        #class_element = self.get_class(name_class)
        class_element["attributes"].append(element_niv1)
        return self

    def delete_attribute_class(self, name_class:str, name_attribute:str) -> None:
        cl, attr=self.get_attribute_class(name_class, name_attribute)
        cl["attributes"].remove(attr)

    def add_association():
        pass

    def delete_association():
        pass

    def add_enumeration():
        pass

    def delete_enumeration():
        pass

    def add_value_enumeration():
        pass

    def delete_value_enumeration():
        pass

if __name__=="__main__":
    sem= SemanticModel()
    sem.read("semantic_model.json")
    print(sem.isAtomic())

    #print(sem.classes)