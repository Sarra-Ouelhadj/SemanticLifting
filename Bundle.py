from library import helpers as h
import copy
from SemanticModel import SemanticModel
import subprocess
from library import generateOntology as onto
import pandas as pd

class Bundle :
    
    semantic_model : SemanticModel
    dataset: str

    def __init__(self, semantic_model : SemanticModel, dataset: str) -> None:
        self.semantic_model=semantic_model
        self.dataset=dataset

    def read_jsonSchema_geojsonData(schema_path:str, dataset_path:str, schema_title:str="exemple"):
        semantic_model=SemanticModel.initiate_from_jsonSchema(schema_url=schema_path,title=schema_title)
        dataset=dataset_path
        return Bundle(semantic_model, dataset)

    def annotate(self, class_:dict=None, attributes:dict=None, enumerations:dict=None, enum_values:dict=None, associations:dict=None):
        self.semantic_model.annotate(class_=class_, attributes=attributes, enumerations=enumerations, enum_values=enum_values, associations=associations)

    def write_rdf (self, ontology_path:str="./results/ontology.ttl", vocabulary_path:str="./results/vocabulary.ttl", instance_path:str="./results/instance.ttl",
                    ontology_namespace = "https://data.grandlyon.com/onto/", 
                    vocabulary_namespace ="https://data.grandlyon.com/vocab/", 
                    instances_namespace = "https://data.grandlyon.com/id/") :

        onto.generateOntology(self.semantic_model,ontology_path,vocabulary_path,ontology_namespace,vocabulary_namespace)
        self.generateSparqlGenerateQuery(vocabulary_namespace, instances_namespace)
        subprocess.run('java -jar ./sparql-generate*.jar --query-file query.rqg --output '+instance_path, shell=True)

    def generateSparqlGenerateQuery (self, vocabulary_namespace :str, instances_namespace :str) :
        """generate SPARQL Generate query"""

        s = """PREFIX iter: <http://w3id.org/sparql-generate/iter/>
        PREFIX fun: <http://w3id.org/sparql-generate/fn/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        GENERATE {\n"""
        
        #iterate over classes
        for list in self.semantic_model.classes:
            s+=("?{} a <{}>".format(h.convertToPascalcase(list["name"]),list["IRI"]))+ ";\n"

            #iterate over attributes
            l=len(list["attributes"])
            for i , attr in enumerate(list["attributes"]):
                s+=("\t<{}> ?{}".format(attr["IRI"],h.convertToPascalcase(attr["name"])))
                s+=";\n" if (i<l-1) else ".\n"
        
        #iterate over associations
        for list in self.semantic_model.associations:
            s += ("?{} <{}> ?{}".format(h.convertToPascalcase(list["source"]),list["IRI"],h.convertToPascalcase(list["destination"]))) + ".\n"
        
        s+=("}} \n SOURCE <{}> AS ?source \nITERATOR iter:GeoJSON(?source) AS ?geometricCoordinates ?properties \n WHERE {{\n".format(self.dataset))

        #bindings
        for list in self.semantic_model.classes:
            for attr in list["attributes"]:
                s+=('BIND (fun:JSONPath(?properties,"$.{}") AS ?{})\n'.format(attr["source"], h.convertToPascalcase(attr["name"]))) 
                if (attr["id"]=="oui") :
                    s+=('BIND(IRI(CONCAT("{}/",fun:JSONPath(?properties,"$.{}"))) AS ?{})\n'.format(instances_namespace+ h.convertToPascalcase(list["name"]),attr["source"],h.convertToPascalcase(list["name"])))
            
        for enum in self.semantic_model.enumerations:
            s+=('BIND(IRI(CONCAT("{}",REPLACE(LCASE(fun:JSONPath(?properties,"$.{}"))," ","_"))) AS ?{})\n'.format(vocabulary_namespace,enum["source"],h.convertToPascalcase(enum["name"])))
        
        s+= "}\n"
        with open("query.rqg", 'w') as fp:
            fp.write(s)

    def split(self,new_class_name:str,class_id: str, class_attributes:list,class_association_new_class:str,IRI: str = "", definition : str = "",enumerations:list=[]):
        """
        >>> b1=b0.split(new_class_name = 'Commune', class_id='code_com_d', class_attributes = ['code_com_g'],
                class_association_new_class='traverseCommuneADroite', definition="Division administrative de la Métropole de Lyon")
        """
        if (IRI == "" and definition == ""):
            raise Exception("IRI or definition parameter must be passed!")
        else :
            d={}
            d["classes"]=[]
            d["associations"]=[]
            d["enumerations"]=[]

            semantic_model = SemanticModel(d)
            
            attributes=[]
            attr_elem = copy.deepcopy(self.semantic_model.get_id())
            attr_elem['id']="non" # clé étrangère
            attributes.append(attr_elem)

            attr_elem = self.semantic_model.get_attribute(class_id)
            self.semantic_model.classes[0]['attributes'].remove(attr_elem) # MAJ du bundle initial
            attr_elem['id']="oui"
            attributes.append(attr_elem)

            for attr_name in class_attributes:
                attr_elem = self.semantic_model.get_attribute(attr_name)
                self.semantic_model.classes[0]['attributes'].remove(attr_elem) # MAJ du bundle initial
                attributes.append(attr_elem)

            semantic_model.add_class(new_class_name,IRI, definition,attributes)

            if (enumerations != []) :
                for enum_name in enumerations :
                    enum_temp = self.semantic_model.get_enumeration(enum_name)
                    self.semantic_model.enumerations.remove(enum_temp) # MAJ du bundle initial
                    semantic_model.enumerations.append(enum_temp)
                    for ass in self.semantic_model.associations :
                        if (ass['destination'] == enum_name + "_options"):
                            self.semantic_model.associations.remove(ass) # MAJ du bundle initial
                            ass['source'] = new_class_name
                            semantic_model.associations.append(ass)
            
            return Bundle(semantic_model, self.dataset)

    #TODO
    def read_tableSchema_csvData(schema_path:str, dataset_path:str):
        ...

    #TODO
    def read_from_csvData():
        ...
    #TODO
    def read_from_geojsonData():
        ...
    
    #TODO
    def read_from_jsonData():
        ...

