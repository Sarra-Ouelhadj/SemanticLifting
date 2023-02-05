from library import helpers as h
from rdflib.namespace import RDF, RDFS, OWL, SKOS
from rdflib import Graph, Literal, URIRef, Namespace
from SemanticModel import SemanticModel

def generateOntology(semantic_model : SemanticModel,ontology_path:str, vocabulary_path:str,
                    ontology_namespace : str, vocabulary_namespace : str):
    """generate ontology files from the semantic model"""

    VS = Namespace("http://www.w3.org/2003/06/sw-vocab-status/ns#")
    g = Graph()
    g2 = Graph ()
    
    #------------------------
    #Classes
    #------------------------
    if (semantic_model.classes[0]['IRI']==''):
        classeURI = URIRef(ontology_namespace + h.convertToPascalcase(semantic_model.classes[0]['name']))

        semantic_model.annotate(class_=str(classeURI))
        
        g.add((classeURI,RDF.type, OWL.Class))    
        g.add((classeURI,RDFS.label, Literal(semantic_model.classes[0]["name"])))
        g.add((classeURI,RDFS.comment, Literal(semantic_model.classes[0]["definition"])))
        g.add((classeURI,RDFS.isDefinedBy, URIRef(ontology_namespace)))
        g.add((classeURI,VS.term_status, Literal("testing")))

    #------------------------
    #Data Properties
    #------------------------
    for attr in filter (lambda value: False if value["IRI"]!='' else True,semantic_model.classes[0]["attributes"]):
        attributeURI = URIRef(ontology_namespace + h.convertToCamelcase(attr["name"]))

        semantic_model.annotate(attributes={attr["name"]:str(attributeURI)})

        g.add((attributeURI,RDF.type, OWL.DatatypeProperty))    
        g.add((attributeURI,RDFS.label, Literal(attr["name"])))
        g.add((attributeURI,RDFS.comment, Literal(attr["definition"])))
        g.add((attributeURI,RDFS.isDefinedBy, URIRef(ontology_namespace)))
        g.add((attributeURI,VS.term_status, Literal("testing")))

    #------------------------
    #Object Properties
    #------------------------
    for ass in filter (lambda value: False if value["IRI"]!='' else True,semantic_model.associations):
        associationURI = URIRef(ontology_namespace + h.convertToCamelcase(ass["name"]))

        semantic_model.annotate(associations={ass["name"]:str(associationURI)})
        
        g.add((associationURI,RDF.type, OWL.ObjectProperty))    
        g.add((associationURI,RDFS.label, Literal(ass["name"])))
        g.add((associationURI,RDFS.comment, Literal(ass["definition"])))
        g.add((associationURI,RDFS.isDefinedBy, URIRef(ontology_namespace)))
        g.add((associationURI,VS.term_status, Literal("testing")))

    #------------------------
    #Individuals
    #------------------------
    for enum in semantic_model.enumerations:
        if enum["IRI"]!="":
            enumerationURI = URIRef(enum["IRI"])
        else :
            enumerationURI = URIRef(vocabulary_namespace + h.convertToPascalcase(enum["name"]))

            semantic_model.annotate(enumerations={enum["name"]:str(enumerationURI)})

            g2.add((enumerationURI, RDF.type, SKOS.ConceptScheme))
            g2.add((enumerationURI,SKOS.prefLabel, Literal(enum["name"])))
            g2.add((enumerationURI,SKOS.definition, Literal(enum["definition"])))
            g2.add((enumerationURI,RDFS.isDefinedBy, URIRef(vocabulary_namespace)))
            g2.add((enumerationURI,VS.term_status, Literal("testing")))
            
        for val in filter(lambda value: False if value["IRI"]!="" else True, enum["values"]):     
            valueURI = URIRef(vocabulary_namespace + h.convertToSnakecase(val["name"]))

            semantic_model.annotate(enum_values={(enum["name"],val["name"]):str(valueURI)})

            g2.add((valueURI,RDF.type, SKOS.Concept))    
            g2.add((valueURI,SKOS.prefLabel, Literal(val["name"])))
            g2.add((valueURI,SKOS.definition, Literal(val["definition"])))
            g2.add((valueURI,RDFS.isDefinedBy, URIRef(vocabulary_namespace)))
            g2.add((valueURI,SKOS.inScheme, enumerationURI))
            g2.add((valueURI,VS.term_status, Literal("testing")))

    with open(ontology_path, 'w') as fo, open(vocabulary_path, 'w') as fv :
        fo.write(g.serialize(format="turtle"))
        fv.write(g2.serialize(format="turtle"))

