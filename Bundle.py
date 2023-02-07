from library import helpers as h
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

