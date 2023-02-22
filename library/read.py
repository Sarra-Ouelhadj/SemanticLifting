from BundleClass import BundleClass
from BundleCollection import BundleCollection
from BundleEnum import BundleEnum
from SemanticModel import SemanticModel
import geopandas as gpd

def read_jsonSchema_geojsonData(schema_path:str, dataset_path:str, schema_title:str="exemple") -> list:
    semantic_model=SemanticModel.initiate_from_jsonSchema(schema_url=schema_path,title=schema_title)
    dataset=gpd.read_file(dataset_path)
    root_bundle = BundleClass(semantic_model, dataset)
    BundleCollection(root_bundle)
    
    if (semantic_model.isAtomic() == False):
        for enum_elem in semantic_model.enumerations:
            d={}
            d["classes"]=[]
            d["associations"]=[]
            d["enumerations"]=[]
            
            semantic_model.enumerations.remove(enum_elem) # MAJ du modèle sémantique initial
            d["enumerations"].append(enum_elem)
            enum_dataset = dataset[enum_elem['source']].to_frame()
            ass = semantic_model.get_association(destination=enum_elem['name'])
            d["associations"].append(ass)
            new_bundle = BundleEnum(SemanticModel(d),enum_dataset)
            BundleCollection.add_bundle(root_bundle, new_bundle, ass['name'], operation="creation")
    
    return BundleCollection.list_bundles()

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