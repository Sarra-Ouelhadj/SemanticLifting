import requests

def initiateSemanticModelFromJsonSchema(schema_url: str, title:str) -> dict:

    response = requests.get(schema_url)
    schema = response.json()

    d={}
    d["classes"]=[]
    d["associations"]=[]
    d["enumerations"]=[]

    class_element={}
    class_element["name"]= title
    class_element["definition"]= ""
    class_element["IRI"]= ""
    class_element["attributes"]=[]
    id_detected= False

    attributes = schema["properties"]["features"]["items"]["properties"]["properties"]["properties"]

    for attr_elem in attributes:
        element_niv1={}
        element_niv1["IRI"]= ""
        element_niv1["source"]= attr_elem    
        
        # le champs "description" est obligatoire
        if 'description' in attributes[attr_elem]:
            element_niv1["definition"]= attributes[attr_elem]["description"]
        elif ('items' in attributes[attr_elem] and 'description' in attributes[attr_elem]["items"]):
            element_niv1["definition"]=attributes[attr_elem]["items"]["description"]
        else : element_niv1["definition"]="une définition exemple"

        if 'type' in attributes[attr_elem]: #nouveau ajout
            element_niv1["type"]= attributes[attr_elem]["type"]

        if 'example' in attributes[attr_elem]: #nouveau ajout
            element_niv1["example"]= attributes[attr_elem]["example"]

        if 'pattern' in attributes[attr_elem]: #nouveau ajout
            element_niv1["pattern"]= attributes[attr_elem]["pattern"]
        
        #nouveau ajout    
        element_niv1["required"] = "oui" if attr_elem in schema["properties"]["features"]["items"]["properties"]["properties"]["required"] else "non"


        if 'enum' not in attributes[attr_elem]: # c'est un attribut
            element_niv1["name"] = attr_elem
            element_niv1["id"]= "non"
            
            if (not id_detected and attr_elem == schema["properties"]["features"]["items"]["properties"]["properties"]["required"][0]):
                element_niv1["id"]= "oui"
                id_detected = True
            
            class_element["attributes"].append(element_niv1)
        
        else: # c'est une énumération
            element_niv1["name"] = attr_elem + "_options" #création du type énuméré
            
            #création de l'association entre la classe et le type énuméré
            ass_elem={}
            ass_elem["name"]="aPour"+ attr_elem
            ass_elem["source"]=class_element["name"]
            ass_elem["destination"]=element_niv1["name"]
            ass_elem["definition"]=""
            ass_elem["IRI"]=""
            d["associations"].append(ass_elem)
            
            #valeurs du type énuméré
            element_niv1["values"]=[]
            for enum_value in attributes[attr_elem]["enum"]:
                enum_elem={}
                enum_elem["name"]=enum_value
                enum_elem["definition"]=""
                enum_elem["IRI"]=""
                element_niv1["values"].append(enum_elem)
                
            d["enumerations"].append(element_niv1)

    d["classes"].append(class_element)

    return d

if __name__ == "__main__":
    schema_url = "https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json"
    title = "AmenagementCyclable"
    print(initiateSemanticModelFromJsonSchema(schema_url, title))


