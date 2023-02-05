from SemanticModel import SemanticModel
import subprocess
from library import generateOntology as onto, generateSparqlGenerateQuery as q
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

    #TODO
    def write_rdf (self, query_path:str, ontology_path:str, vocabulary_path:str, instance_path:str,
                    ontology_namespace = "https://data.grandlyon.com/onto/", 
                    vocabulary_namespace ="https://data.grandlyon.com/vocab/", 
                    instances_namespace = "https://data.grandlyon.com/id/") :
        """generate RDF data from SPARQL Generate query"""

        onto.generateOntology(self.semantic_model,ontology_path,vocabulary_path,ontology_namespace,vocabulary_namespace)
        query_file=q.generateSparqlGenerateQuery(self,query_path,vocabulary_namespace, instances_namespace)

        subprocess.run('java -jar /home/sarra/Documents/Doctorat/Python/SemanticLifting2/sparql-generate*.jar --query-file '+ query_file+' --output '+instance_path, shell=True)

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

# ---------------------------------
schema = "https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json"
titre = "AmenagementCyclable"
dataset="https://www.data.gouv.fr/fr/datasets/r/9ca17d67-3ba3-410b-9e32-6ac7948c3e06"

b0=Bundle.read_jsonSchema_geojsonData(schema,dataset,titre)
b0.annotate(attributes={"nom_loc":"http://schema.org/name"},
            class_={"AmenagementCyclable":"http://schema.org/Thing"},
            associations={"aPourreseau_loc":"http://exemple/aPourreseau_loc"},
            enum_values={("reseau_loc_options","REV"):"http://exemple/REV"}
)

ontology_path="/home/sarra/Documents/Doctorat/Python/SemanticLifting2/ontology.ttl"
vocabulary_path="/home/sarra/Documents/Doctorat/Python/SemanticLifting2/vocabulary.ttl"
instance_path="/home/sarra/Documents/Doctorat/Python/SemanticLifting2/instance.ttl"
query_path="/home/sarra/Documents/Doctorat/Python/SemanticLifting2/query.rq"

#b0.write_rdf(query_path,ontology_path,vocabulary_path,instance_path)

