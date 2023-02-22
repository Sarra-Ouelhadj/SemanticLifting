import copy
import subprocess
from BundleCollection import BundleCollection
from SemanticModel import SemanticModel
import json
from library.initiateSemanticModelFromJsonSchema import *
from library import helpers as h
from rdflib.namespace import RDF, RDFS, OWL, SKOS
from rdflib import Graph, Literal, URIRef, Namespace
from Bundle import Bundle
import geopandas as gpd

class BundleClass(Bundle):
    
    def annotate(self, class_:dict=None, attributes:dict=None):
        """
        >>> annotate(class_={"AmenagementCyclable":"http://schema.org/Thing"})
        >>> annotate(attributes={"nom_loc":"http://schema.org/name", "num_iti":"http://schema.org/name"})
        >>> annotate(associations={"reseau_loc":"http://exemple/reseau_loc"})
        """
        args = locals()
        if (any(args.values())==True):
            if (class_!=None):
                self.semantic_model.classes[0]['IRI']=class_[self.semantic_model.classes[0]['name']]

            if (attributes!=None):
                attributes_keys = list(attributes.keys())
                for value in attributes_keys: 
                    i=self.semantic_model.index(self.semantic_model.classes[0]['attributes'],'name', value)
                    #affecter l'IRI
                    self.semantic_model.classes[0]['attributes'][i]['IRI']=attributes[value]
        else:
            raise ValueError('Au moins un paramètre par défaut doit être passé !')
    
    def validate(self):
        """
        class validation \n
        0. Le modèle sémantique doit contenir au moins une classe
        1. Chaque classe doit avoir un nom
        2. Chaque classe doit avoir un lien de référence ou une définition

        attributes validation \n
        0. Chaque attribut doit avoir un nom
        1. Chaque attribut doit avoir un lien de référence ou une définition
        2. Chaque attribut doit avoir une source
        3. Le champs identifiant n'est pas vide
        4. Chaque classe doit avoir au minimum un identifiant
        5. Pas d'attributs avec le même nom dans le modèle sémantique
        """
        errors = []

        #------------------------
        #classes validation
        #------------------------

        #0. Le modèle sémantique doit contenir au moins une classe
        if (len(self.semantic_model.classes)==0) : errors.append ("Le modèle sémantique doit contenir au moins une classe")
        
        for cl in self.semantic_model.classes: 
            #1. Chaque classe doit avoir un nom
            if (cl['name']=='' or cl['name']== None): errors.append ("Le nom de la classe est obligatoire") 
            
            #2. Chaque classe doit avoir un lien de référence ou une définition
            if ((cl['IRI']=='' or cl['IRI']== None) and (cl['definition']=='' or cl['definition'] == None )): errors.append (f"La classe {cl['name']} doit avoir un lien de référence ou une définition") 

            #------------------------
            #attributes validation
            #------------------------

            attribute_total_number = 0
            set_of_attributes = set()
            list=[]

            for attr in cl['attributes']:
                #0. Chaque attribut doit avoir un nom
                if (attr['name']=='' or attr['name']== None) : errors.append ("Le nom de l'attribut est obligatoire")

                #1. Chaque attribut doit avoir un lien de référence ou une définition
                if ((attr['IRI']=='' or attr['IRI']== None) and (attr['definition']=='' or attr['definition'] == None )): errors.append (f"L'attribut {attr['name']} doit avoir un lien de référence ou une définition")
                
                #2. Chaque attribut doit avoir une source
                if (attr['source']=='' or attr['source']== None): errors.append (f"L'attribut {attr['name']} doit avoir une source")

                #3. Le champs identifiant n'est pas vide
                if (attr['id']=='' or attr['id']== None): errors.append (f"Le champs 'Identifiant' n'est pas précisé pour l'attribut {attr['name']}")            
                
                list.append(attr['id'])
                attribute_total_number+=1
                set_of_attributes.add(attr['name'])
            
            #4. Chaque classe doit avoir au minimum un identifiant
            if ("oui" not in list) : errors.append (f"la classe {cl['name']} n'a pas d'identifiant")

            #5. Pas d'attributs avec le même nom dans le modèle sémantique
            if len(set_of_attributes)< attribute_total_number : errors.append(f"Des attributs de même nom existent dans le modèle sémantique")
        
        self.validate_association()

        if errors:
            raise Exception (errors)
        else : return True

    def generateOntology(self, ontology_path:str):
        """generate ontology files from the semantic model"""

        VS = Namespace("http://www.w3.org/2003/06/sw-vocab-status/ns#")
        g = Graph()
        
        #------------------------
        #Classes
        #------------------------
        if (self.semantic_model.classes[0]['IRI']==''):
            classeURI = URIRef(self.semantic_model.ontology_namespace + h.convertToPascalcase(self.semantic_model.classes[0]['name']))

            self.annotate(class_={self.semantic_model.classes[0]['name']:str(classeURI)})
            
            g.add((classeURI,RDF.type, OWL.Class))    
            g.add((classeURI,RDFS.label, Literal(self.semantic_model.classes[0]["name"])))
            g.add((classeURI,RDFS.comment, Literal(self.semantic_model.classes[0]["definition"])))
            g.add((classeURI,RDFS.isDefinedBy, URIRef(self.semantic_model.ontology_namespace)))
            g.add((classeURI,VS.term_status, Literal("testing")))

        #------------------------
        #Data Properties
        #------------------------
        for attr in filter (lambda value: False if value["IRI"]!='' else True,self.semantic_model.classes[0]["attributes"]):
            attributeURI = URIRef(self.semantic_model.ontology_namespace + h.convertToCamelcase(attr["name"]))

            self.annotate(attributes={attr["name"]:str(attributeURI)})

            g.add((attributeURI,RDF.type, OWL.DatatypeProperty))    
            g.add((attributeURI,RDFS.label, Literal(attr["name"])))
            g.add((attributeURI,RDFS.comment, Literal(attr["definition"])))
            g.add((attributeURI,RDFS.isDefinedBy, URIRef(self.semantic_model.ontology_namespace)))
            g.add((attributeURI,VS.term_status, Literal("testing")))

        #------------------------
        #Object Properties
        #------------------------
        for ass in filter (lambda value: False if value["IRI"]!='' else True,self.semantic_model.associations):
            associationURI = URIRef(self.semantic_model.ontology_namespace + h.convertToCamelcase(ass["name"]))

            self.annotate(associations={ass["name"]:str(associationURI)})
            
            g.add((associationURI,RDF.type, OWL.ObjectProperty))    
            g.add((associationURI,RDFS.label, Literal(ass["name"])))
            g.add((associationURI,RDFS.comment, Literal(ass["definition"])))
            g.add((associationURI,RDFS.isDefinedBy, URIRef(self.semantic_model.ontology_namespace)))
            g.add((associationURI,VS.term_status, Literal("testing")))

        with open(ontology_path, 'w') as fo :
            fo.write(g.serialize(format="turtle"))

    # --------------------------
    def write_rdf (self, instance_path:str="./results/instance.ttl") :
        if (self.validate()):
            self.generateSparqlGenerateQuery(self.semantic_model.vocabulary_namespace, self.instances_namespace)
            result = subprocess.run('java -jar ./sparql-generate*.jar --query-file query.rqg --output '+instance_path, shell=True ,capture_output=True, text=True)
            with open('./results/out.log','w') as fout,  open('./results/err.log','w') as ferr :
                fout.write(result.stdout)
                ferr.write(result.stderr)

    def recursive_gen(self, s, dataset):
        
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
            bun = BundleCollection.get_neighbour(self, list['name'])
            if (isinstance(bun, BundleClass)):
                dataset = self.dataset.merge(bun.dataset, left_on=self.semantic_model.get_id()['source'], right_on=bun.semantic_model.get_id()['source'])
                s, dataset = bun.recursive_gen(s, dataset)

            s += ("?{} <{}> ?{}".format(h.convertToPascalcase(list["source"]),list["IRI"],h.convertToPascalcase(list["destination"]))) + ".\n"
        return s, dataset
        
    
    def generateSparqlGenerateQuery (self) :
        """generate SPARQL Generate query"""

        s = """PREFIX iter: <http://w3id.org/sparql-generate/iter/>
        PREFIX fun: <http://w3id.org/sparql-generate/fn/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        GENERATE {\n"""

        s, dataset = self.recursive_gen(s, self.dataset)
        dataset_path = "./results/data.geojson"
        dataset.to_file(dataset_path, driver="GeoJSON")
        s+=("}} \n SOURCE <{}> AS ?source \nITERATOR iter:GeoJSON(?source) AS ?geometricCoordinates ?properties \n WHERE {{\n".format(dataset_path))

        #bindings
        for list in self.semantic_model.classes:
            for attr in list["attributes"]:
                s+=('BIND (fun:JSONPath(?properties,"$.{}") AS ?{})\n'.format(attr["source"], h.convertToPascalcase(attr["name"]))) 
                if (attr["id"]=="oui") :
                    s+=('BIND(IRI(CONCAT("{}/",fun:JSONPath(?properties,"$.{}"))) AS ?{})\n'.format(self.instances_namespace+ h.convertToPascalcase(list["name"]),attr["source"],h.convertToPascalcase(list["name"])))
            
        for enum in self.semantic_model.enumerations:
            s+=('BIND(IRI(CONCAT("{}",REPLACE(LCASE(fun:JSONPath(?properties,"$.{}"))," ","_"))) AS ?{})\n'.format(self.semantic_model.vocabulary_namespace, enum["source"],h.convertToPascalcase(enum["name"])))
        
        s+= "}\n"
        with open("query.rqg", 'w') as fp:
            fp.write(s)

    def generateSparqlGenerateQuery1 (self, vocabulary_namespace :str, instances_namespace :str) :
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

    def split(self,new_class_name:str,class_id:str, class_attributes:list,predicate:str,enumerations:list=[]):
        """
        >>> b1=b0.split(new_class_name = 'Commune', class_id='code_com_d', class_attributes = ['code_com_g'],
                predicate='traverseCommuneADroite', definition="Division administrative de la Métropole de Lyon")
        """
        d={}
        d["classes"]=[]
        d["associations"]=[]
        d["enumerations"]=[]

        semantic_model = SemanticModel(d)
        
        attributes=[]

        attr_elem = copy.deepcopy(self.semantic_model.get_attribute(class_id)) # clé étrangère
        attr_elem['id']="oui"
        attributes.append(attr_elem)
        new_dataset = self.dataset[attr_elem['source']].to_frame()

        for attr_name in class_attributes:
            attr_elem = self.semantic_model.get_attribute(attr_name)
            self.semantic_model.classes[0]['attributes'].remove(attr_elem) # MAJ du bundle initial
            attributes.append(attr_elem)
            new_dataset = new_dataset.join(self.dataset[attr_elem['source']])

        self.semantic_model.add_association(predicate, self.semantic_model.classes[0]['name'], new_class_name)
        semantic_model.add_class(name=new_class_name,attributes=attributes)
        new_bundle = BundleClass(semantic_model, new_dataset)

        if (enumerations != []) :
            for enum_name in enumerations :
                ass_temp = self.semantic_model.get_association(destination=enum_name)
                
                enumbun = BundleCollection.get_neighbour(self,ass_temp['name'])
                
                enum_temp = enumbun.semantic_model.get_enumeration(enum_name)
                new_dataset = new_dataset.join(self.dataset[enum_temp['source']])
                #il faut que je supprime les enumérations du dataset de la classe originale

                BundleCollection.graph.remove_edge(self, enumbun)
                self.semantic_model.associations.remove(ass_temp)
                
                ass_temp['source']=new_class_name
                semantic_model.associations.append(ass_temp)
                BundleCollection.add_bundle(new_bundle,enumbun,ass_temp['name'])

        BundleCollection.add_bundle(origin_bundle=self, new_bundle=new_bundle, predicate=predicate)
 
        return new_bundle