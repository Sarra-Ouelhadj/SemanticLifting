from library import helpers as h
from Bundle import Bundle

def generateSparqlGenerateQuery (bundle : Bundle, query_path:str, vocabulary_namespace :str, instances_namespace :str) :
    """generate SPARQL Generate query"""

    s = """PREFIX iter: <http://w3id.org/sparql-generate/iter/>
    PREFIX fun: <http://w3id.org/sparql-generate/fn/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    GENERATE {\n"""
    
    #iterate over classes
    for list in bundle.semantic_model.classes:
        s+=("?{} a <{}>".format(h.convertToPascalcase(list["name"]),list["IRI"]))+ ";\n"

        #iterate over attributes
        l=len(list["attributes"])
        for i , attr in enumerate(list["attributes"]):
            s+=("\t<{}> ?{}".format(attr["IRI"],h.convertToPascalcase(attr["name"])))
            s+=";\n" if (i<l-1) else ".\n"
    
    #iterate over associations
    for list in bundle.semantic_model.associations:
        s += ("?{} <{}> ?{}".format(h.convertToPascalcase(list["source"]),list["IRI"],h.convertToPascalcase(list["destination"]))) + ".\n"
    
    s+=("}} \n SOURCE <{}> AS ?source \nITERATOR iter:GeoJSON(?source) AS ?geometricCoordinates ?properties \n WHERE {{\n".format(bundle.dataset))

    #bindings
    for list in bundle.semantic_model.classes:
        for attr in list["attributes"]:
            s+=('BIND (fun:JSONPath(?properties,"$.{}") AS ?{})\n'.format(attr["source"], h.convertToPascalcase(attr["name"]))) 
            if (attr["id"]=="oui") :
                s+=('BIND(IRI(CONCAT("{}/",fun:JSONPath(?properties,"$.{}"))) AS ?{})\n'.format(instances_namespace+ h.convertToPascalcase(list["name"]),attr["source"],h.convertToPascalcase(list["name"])))
        
    for enum in bundle.semantic_model.enumerations:
        s+=('BIND(IRI(CONCAT("{}",REPLACE(LCASE(fun:JSONPath(?properties,"$.{}"))," ","_"))) AS ?{})\n'.format(vocabulary_namespace,enum["source"],h.convertToPascalcase(enum["name"])))
    
    s+= "}\n"
    with open(query_path, 'w') as fp:
        fp.write(s)
    return query_path