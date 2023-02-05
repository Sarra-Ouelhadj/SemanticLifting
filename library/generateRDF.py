import subprocess
from library import generateSparqlGenerateQuery as q, generateOntology as onto
from Bundle import Bundle

def generateRDF (bundle : Bundle, query_path:str, ontology_path:str, vocabulary_path:str, instance_path:str,
                ontology_namespace, vocabulary_namespace, instances_namespace) :
    """generate RDF data from SPARQL Generate query"""

    onto.generateOntology(bundle.semantic_model,ontology_path,vocabulary_path,ontology_namespace,vocabulary_namespace)
    query_file=q.generateSparqlGenerateQuery(bundle,query_path,vocabulary_namespace, instances_namespace)

    subprocess.run('java -jar /home/sarra/Documents/Doctorat/Python/SemanticLifting2/sparql-generate*.jar --query-file '+ query_file+' --output '+instance_path, shell=True)