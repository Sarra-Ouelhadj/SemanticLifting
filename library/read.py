import requests
from BundleClass import BundleClass
from BundleEnum import BundleEnum
from BundleCollection import BundleCollection
import geopandas as gpd
from library import helpers as h

def read_jsonSchema_geojsonData(schema_path:str, dataset_path:str, schema_title:str="exemple") -> BundleClass:
    """
    initialize a first BundleClass with its dangling BundleEnums if enums exist, from a schema developped by schema.data.gouv.fr
    of JSON Schema format and from any dataset compliant with it.
     
     Parameters
     ----------
     schema_path : relative, absolute path or URL given as a string
        schema to be converted into the semantic model of the bundles created  
     dataset_path : relative, absolute path or URL given as a string
        dataset to be loaded into a geopandas.geoDataFrame
     schema_title : str
        title labeling the main concept described in the dataset. Ex: "Cycling facilities"

     Returns
     ---------
     Bundle.BundleClass
        BundleClass root created from the couple (schema, compliant dataset)

    """
    
    response = requests.get(schema_path)
    schema = response.json()
    dataset=gpd.read_file(dataset_path, rows = 100)

    class_name = h.convertToPascalcase(schema_title)
    root_bundle = BundleClass(class_name, dataset)

    id_detected= False

    attributes = schema["properties"]["features"]["items"]["properties"]["properties"]["properties"]

    for attr_elem in attributes:
        element_niv1={}
        element_niv1["IRI"]= None
        element_niv1["source"]= attr_elem    
        
        # le champs "description" est obligatoire
        if 'description' in attributes[attr_elem]:
            element_niv1["definition"]= attributes[attr_elem]["description"]
        elif ('items' in attributes[attr_elem] and 'description' in attributes[attr_elem]["items"]):
            element_niv1["definition"]=attributes[attr_elem]["items"]["description"]
        else : element_niv1["definition"] = "une définition exemple"

        if 'type' in attributes[attr_elem]: #nouveau ajout
            element_niv1["type"]= attributes[attr_elem]["type"]

        if 'example' in attributes[attr_elem]: #nouveau ajout
            element_niv1["example"]= attributes[attr_elem]["example"]

        if 'pattern' in attributes[attr_elem]: #nouveau ajout
            element_niv1["pattern"]= attributes[attr_elem]["pattern"]
        
        #nouveau ajout    
        element_niv1["required"] = "oui" if attr_elem in schema["properties"]["features"]["items"]["properties"]["properties"]["required"] else "non"

        element_niv1["name"] = attr_elem

        if 'enum' not in attributes[attr_elem]: # c'est un attribut
            element_niv1["id"]= "non"
            
            if (not id_detected and attr_elem == schema["properties"]["features"]["items"]["properties"]["properties"]["required"][0]):
                element_niv1["id"]= "oui"
                id_detected = True
            
            root_bundle.attributes.append(element_niv1)
        
        else: # c'est une énumération
            new_enum_bundle = BundleEnum(attr_elem, dataset[attr_elem].to_frame(), definition= element_niv1["definition"], linked_to=[])
            new_enum_bundle.source = element_niv1["source"]
            new_enum_bundle.type = element_niv1["type"]
            new_enum_bundle.required = element_niv1["required"]

            #création de l'association entre la classe et le type énuméré
            ass_elem={}
            ass_elem["name"]=attr_elem
            ass_elem["source"]=root_bundle
            ass_elem["destination"]=new_enum_bundle
            ass_elem["definition"]= element_niv1["definition"]
            ass_elem["IRI"]=None
            
            root_bundle.linked_to.append(ass_elem)
            
            #valeurs du type énuméré
            for enum_value in attributes[attr_elem]["enum"]:
                enum_elem={}
                enum_elem["name"]=enum_value
                enum_elem["definition"]=None
                enum_elem["IRI"]=None
                new_enum_bundle.values.append(enum_elem)
                
    BundleCollection(root_bundle)
    return root_bundle

#TODO
def read_tableSchema_csvData(schema_path:str, dataset_path:str):
    raise NotImplementedError()

#TODO
def read_from_csvData():
    raise NotImplementedError()

#TODO
def read_from_geojsonData():
    raise NotImplementedError()

#TODO
def read_from_jsonData():
    raise NotImplementedError()
