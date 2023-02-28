import copy
import subprocess
from BundleCollection import BundleCollection
from library import helpers as h
from rdflib.namespace import RDF, RDFS, OWL, SKOS
from rdflib import Graph, Literal, URIRef, Namespace
from Bundle import Bundle
import geopandas as gpd
import pandas as pd

class BundleClass(Bundle):
    
    attributes = []
    
    def __init__(self, name: str, dataset: gpd.GeoDataFrame, IRI=None, definition=None, attributes = [], linked_to=[]) -> None:
        super().__init__(name, dataset, IRI, definition, linked_to)
        self.attributes = attributes

    def show(self, deep = False):
        print("------- Class -------")
        super().show()
        print("\t ------- attributes -------")
        for attr in self.attributes:
            print("\t name :" ,attr["name"])
            print("\t IRI :" ,attr["IRI"])
            print("\t definition :" ,attr["definition"])
            print("\t source :" ,attr["source"])
            print("\t type :" ,attr["type"])
            print("\t id :" ,attr["id"])
            print("\t --------------")
        if (self.linked_to): print("------- Links -------")
        for l in self.linked_to :
            print("name :" ,l["name"])
            print("IRI :" ,l["IRI"])
            print("definition :" ,l["definition"])
            print("source :" ,l["source"])
            if (deep) : 
                l["destination"].show()
            else :
                print("destination :" ,l["destination"].name)
                print("--------------")
        
    def annotate(self, class_IRI:str=None, attributes:dict=None, associations: dict = None):
        """
        >>> annotate(class_IRI="http://schema.org/Thing")
        >>> annotate(attributes={"nom_loc":"http://schema.org/name", "num_iti":"http://schema.org/name"})
        >>> annotate(associations={"reseau_loc":"http://exemple/reseau_loc"})
        """
        args = locals()
        if (any(args.values())==True):
            if (class_IRI!=None):
                self.IRI = class_IRI

            if (attributes!=None):
                attributes_keys = list(attributes.keys())
                for value in attributes_keys: 
                    i=self.index(self.attributes,'name', value)
                    #affecter l'IRI
                    self.attributes[i]['IRI']=attributes[value]
            
            if (associations!=None):
                associations_keys=list(associations.keys())
                for value in associations_keys: 
                    i=self.index(self.linked_to,'name', value)
                    #affecter l'IRI
                    self.linked_to[i]['IRI']=associations[value]
        else:
            raise ValueError('Au moins un paramètre par défaut doit être passé !')
    
    def validate(self, errors = [], deep = False):
        """
        class validation \n
        0. La classe doit avoir un nom
        1. La classe doit avoir un lien de référence ou une définition

        attributes validation \n
        0. Chaque attribut doit avoir un nom
        1. Chaque attribut doit avoir un lien de référence ou une définition
        2. Chaque attribut doit avoir une source
        3. Le champs identifiant n'est pas vide
        4. Chaque classe doit avoir au minimum un identifiant
        5. Pas d'attributs avec le même nom dans le modèle sémantique

        associations validation \n
        0. Chaque association doit avoir un nom
        1. Chaque association doit avoir un lien de référence ou une définition
        2. Chaque association doit avoir une source
        3. Chaque association doit avoir une destination
        """
        errors = errors

        #------------------------
        #classe validation
        #------------------------
        
        #0. La classe doit avoir un nom
        if (self.name == '' or self.name == None): errors.append ("Le nom de la classe est obligatoire") 
        
        #1. La classe doit avoir un lien de référence ou une définition
        if ((self.IRI == '' or self.IRI == None) and (self.definition == '' or self.definition == None )): errors.append (f"La classe {self.name} doit avoir un lien de référence ou une définition") 

        #------------------------
        #attributes validation
        #------------------------

        attribute_total_number = 0
        set_of_attributes = set()
        list=[]

        for attr in self.attributes:
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
        
        #4. La classe doit avoir au minimum un identifiant
        if ("oui" not in list) : errors.append (f"la classe {self.name} n'a pas d'identifiant")

        #5. Pas d'attributs avec le même nom dans le modèle sémantique
        if len(set_of_attributes)< attribute_total_number : errors.append(f"Des attributs de même nom existent dans le modèle sémantique")
    
        #------------------------
        #associations validation
        #------------------------

        for ass in self.linked_to :
            #0. Chaque association doit avoir un nom
            if (ass['name']=='' or ass['name']== None): errors.append ("Le nom de l'association est obligatoire")

            #1. Chaque association doit avoir un lien de référence ou une définition
            if ((ass['IRI']=='' or ass['IRI']== None) and (ass['definition']=='' or ass['definition'] == None )): errors.append(f"L'association {ass['name']} doit avoir un lien de référence ou une définition")

            #2. Chaque association doit avoir une source
            if (ass['source']=='' or ass['source']==None) : errors.append (f"L'association {ass['name']} doit avoir une source")

            #3. Chaque association doit avoir une destination
            if (ass['destination']=='' or ass['destination']==None) : errors.append (f"L'association {ass['name']} doit avoir une destination")

            if (deep) : 
                ass['destination'].validate(errors, False)
        
        try :
            if errors:
                raise Exception (errors)
            else : return True
        except Exception as e :
            raise e

    def document(self, class_definition : str = None, attributes:dict = None, associations:dict = None):
        """
        >>> document(associations = {'aPourProfession' : 'La profession de la personne'})
        """
        args = locals()
        if (any(args.values())==True):
            if (class_definition != None):
                self.definition = class_definition
        
            if (attributes != None) :
                attributes_keys = list(attributes.keys())
                for value in attributes_keys:
                    i=self.index(self.attributes, 'name', value)
                    # donner une définition
                    self.attributes[i]['definition']= attributes[value]

            if (associations!=None):
                associations_keys=list(associations.keys())
                for value in associations_keys: 
                    i=self.index(self.linked_to,'name', value)
                    # donner une définition
                    self.linked_to[i]['definition']=associations[value]
        else:
            raise ValueError('Au moins un paramètre par défaut doit être passé !')

    def generateOntology(self, ontology_path:str, deep = False, ontology_graph = Graph(), kpi_results = pd.DataFrame()):
        """generate ontology files from the semantic model"""

        VS = Namespace("http://www.w3.org/2003/06/sw-vocab-status/ns#")
        g = ontology_graph
        
        class_created = False

        #------------------------
        #Classes
        #------------------------
        if (self.IRI =='' or self.IRI == None):
            classeURI = URIRef(self.ontology_namespace + h.convertToPascalcase(self.name))

            self.annotate(class_IRI=str(classeURI))
            
            g.add((classeURI,RDF.type, OWL.Class))    
            g.add((classeURI,RDFS.label, Literal(self.name)))
            g.add((classeURI,RDFS.comment, Literal(self.definition)))
            g.add((classeURI,RDFS.isDefinedBy, URIRef(self.ontology_namespace)))
            g.add((classeURI,VS.term_status, Literal("testing")))
            
            class_created = True

            if (deep):
                df = pd.DataFrame({
                    "IRI" : str(classeURI),
                    "type": pd.Categorical(["Class"]),
                    "related": "NA"
                })
                
                kpi_results = pd.concat([kpi_results,df],ignore_index=True)
            
        #------------------------
        #Data Properties
        #------------------------
        for attr in filter (lambda value: False if (value["IRI"]!='' and value["IRI"]!=None) else True, self.attributes):
            attributeURI = URIRef(self.ontology_namespace + h.convertToCamelcase(attr["name"]))

            self.annotate(attributes={attr["name"]:str(attributeURI)})

            g.add((attributeURI,RDF.type, OWL.DatatypeProperty))    
            g.add((attributeURI,RDFS.label, Literal(attr["name"])))
            g.add((attributeURI,RDFS.comment, Literal(attr["definition"])))
            g.add((attributeURI,RDFS.isDefinedBy, URIRef(self.ontology_namespace)))
            g.add((attributeURI,VS.term_status, Literal("testing")))
            
            df = pd.DataFrame({
                "IRI" : str(attributeURI),
                "type": pd.Categorical(["DatatypeProperty"]),
                "related": self.name
            })
            
            kpi_results = pd.concat([kpi_results,df],ignore_index=True)

        #------------------------
        #Object Properties
        #------------------------
        for ass in filter (lambda value: False if (value["IRI"]!='' and value["IRI"]!=None) else True, self.linked_to):
            associationURI = URIRef(self.ontology_namespace + h.convertToCamelcase(ass["name"]))

            self.annotate(associations={ass["name"]:str(associationURI)})
            
            g.add((associationURI,RDF.type, OWL.ObjectProperty))    
            g.add((associationURI,RDFS.label, Literal(ass["name"])))
            g.add((associationURI,RDFS.comment, Literal(ass["definition"])))
            g.add((associationURI,RDFS.isDefinedBy, URIRef(self.ontology_namespace)))
            g.add((associationURI,VS.term_status, Literal("testing")))
            
            df = pd.DataFrame({
                "IRI" : str(associationURI),
                "type": pd.Categorical(["ObjectProperty"]),
                "related": self.name
            })
            
            kpi_results = pd.concat([kpi_results,df],ignore_index=True)


            if (deep):
                 g, kpi_results = ass['destination'].generateOntology(ontology_path, False, g, kpi_results)

        
        if (deep==False and class_created) :
            print(f"L'IRI de la classe `{self.name}` a été créé : {self.IRI}")
            
        if (deep==False):
            print(f"Le nombre de DatatypeProperties créées pour la classe `{self.name}` : {kpi_results.loc[kpi_results['type']=='DatatypeProperty', 'IRI'].count()}")
            print(f"Le nombre d'ObjectProperties créés pour la classe `{self.name}` : {kpi_results.loc[kpi_results['type']=='ObjectProperty', 'IRI'].count()}")

        with open(ontology_path, 'a') as fo :
            fo.write(g.serialize(format="turtle"))

        if (deep and BundleCollection.root is self):
        
            # Le nombre de classes créées au total 
            nb_cl = kpi_results.loc[kpi_results['type']=='Class', 'IRI'].count()
            print("Le nombre de classes créées au total : ", nb_cl)
            
            # Le nombre de DatatypeProperties créées au total 
            print("Le nombre de DatatypeProperties créées au total : ",kpi_results.loc[kpi_results['type']=='DatatypeProperty', 'IRI'].count())
            
            # Le nombre d'ObjectProperties créés au total
            print("Le nombre d'ObjectProperties créés au total : ",kpi_results.loc[kpi_results['type']=='ObjectProperty', 'IRI'].count())
            
            # Le nombre de ConceptSchemes (énumérations) créés au total
            nb_csch = kpi_results.loc[kpi_results['type']=='ConceptScheme', 'IRI'].count()
            print("Le nombre de ConceptSchemes (énumérations) créés au total : ", nb_csch)
            
            # Le nombre de Concepts (valeurs d'énumération) créés au total
            print("Le nombre de Concepts (valeurs d'énumération) créés au total : ",kpi_results.loc[kpi_results['type']=='Concept', 'IRI'].count())
            
            if (nb_cl > 1) :
                # Le nombre de DatatypeProperties créées par classe
                print("Le nombre de DatatypeProperties créées par classe : \n",kpi_results.loc[kpi_results['type']=='DatatypeProperty', ['IRI', 'related']].groupby('related')['IRI'].count().to_frame())
                
                # Le nombre d'ObjectProperties créés par classe
                print("Le nombre d'ObjectProperties créés par classe : \n",kpi_results.loc[kpi_results['type']=='ObjectProperty', ['IRI', 'related']].groupby('related')['IRI'].count().to_frame())
                
            if (nb_csch > 1) :
                # Le nombre de Concepts créés par ConceptSchemes
                print("Le nombre de Concepts créés par ConceptSchemes : \n",kpi_results.loc[kpi_results['type']=='Concept', ['IRI', 'related']].groupby('related')['IRI'].count().to_frame())

        if (deep) : return g, kpi_results

    def write_rdf(self, instance_path:str="./results/instances.ttl", ontology_path:str = "./results/ontology.ttl", deep = False) :
        
        if (self.validate(deep=deep)):
            self.generateSparqlGenerateQuery1(deep=deep)
            result = subprocess.run('java -jar ./sparql-generate*.jar --query-file query.rqg --output '+instance_path, shell=True ,capture_output=True, text=True)
            with open('./results/out.log','w') as fout,  open('./results/err.log','w') as ferr :
                fout.write(result.stdout)
                ferr.write(result.stderr)

    def recursive_gen_part1(self, s1, dataset, s2="", deep = False):
        
        #iterate over classes
        s1+=("?{} a <{}>".format(h.convertToPascalcase(self.name), self.IRI))+ ";\n"

        #iterate over attributes
        l=len(self.attributes)
        for i , attr in enumerate(self.attributes):
            s1+=("\t<{}> ?{}".format(attr["IRI"],h.convertToPascalcase(attr["name"])))
            s1+=";\n" if (i<l-1) else ".\n"
        
        #bindings attributes
            s2+=('BIND (fun:JSONPath(?properties,"$.{}") AS ?{})\n'.format(attr["source"], h.convertToPascalcase(attr["name"]))) 
            if (attr["id"]=="oui") :
                s2+=('BIND(IRI(CONCAT("{}/",fun:JSONPath(?properties,"$.{}"))) AS ?{})\n'.format(self.instances_namespace+ h.convertToPascalcase(self.name),attr["source"],h.convertToPascalcase(self.name)))
 
        #iterate over associations
        for l in self.linked_to:
            if (type(l["destination"])!=type(self)): # c'est une énumération
                s1 += ("?{} <{}> ?{}".format(h.convertToPascalcase(self.name),l["IRI"],h.convertToPascalcase(l["destination"].name))) + ".\n"

                # bindings enumerations
                s2+=('BIND(IRI(CONCAT("{}",REPLACE(LCASE(fun:JSONPath(?properties,"$.{}"))," ","_"))) AS ?{})\n'.format(self.vocabulary_namespace, l["destination"].source, h.convertToPascalcase(l["destination"].name)))

            else : # c'est une classe
                if (deep):
                    dataset = self.dataset.merge(l["destination"].dataset, on=l["destination"].get_id()['source'])

                    s1, s2, dataset = l["destination"].recursive_gen_part1(s1, dataset, s2, True)
                    s1 += ("?{} <{}> ?{}".format(h.convertToPascalcase(self.name),l["IRI"],h.convertToPascalcase(l["destination"].name))) + ".\n"


        return s1, s2, dataset

    def generateSparqlGenerateQuery (self) :
        """generate SPARQL Generate query"""

        s = """PREFIX iter: <http://w3id.org/sparql-generate/iter/>
        PREFIX fun: <http://w3id.org/sparql-generate/fn/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        GENERATE {\n"""
        
        #iterate over classes
        s+=("?{} a <{}>".format(h.convertToPascalcase(self.name), self.IRI))+ ";\n"

        #iterate over attributes
        l=len(self.attributes)
        for i , attr in enumerate(self.attributes):
            s+=("\t<{}> ?{}".format(attr["IRI"],h.convertToPascalcase(attr["name"])))
            s+=";\n" if (i<l-1) else ".\n"
        
        #iterate over associations
        for l in self.linked_to:
            s += ("?{} <{}> ?{}".format(h.convertToPascalcase(self.name),l["IRI"],h.convertToPascalcase(l["destination"].name))) + ".\n"
        
        self.dataset.to_file("./results/data.geojson", driver="GeoJSON")

        s+=("}} \n SOURCE <{}> AS ?source \nITERATOR iter:GeoJSON(?source) AS ?geometricCoordinates ?properties \n WHERE {{\n".format("./results/data.geojson"))

        #bindings
        for attr in self.attributes:
            s+=('BIND (fun:JSONPath(?properties,"$.{}") AS ?{})\n'.format(attr["source"], h.convertToPascalcase(attr["name"]))) 
            if (attr["id"]=="oui") :
                s+=('BIND(IRI(CONCAT("{}/",fun:JSONPath(?properties,"$.{}"))) AS ?{})\n'.format(self.instances_namespace+ h.convertToPascalcase(self.name),attr["source"],h.convertToPascalcase(self.name)))
            
        for l in self.linked_to:
            s+=('BIND(IRI(CONCAT("{}",REPLACE(LCASE(fun:JSONPath(?properties,"$.{}"))," ","_"))) AS ?{})\n'.format(self.vocabulary_namespace, l["destination"].source, h.convertToPascalcase(l["destination"].name)))
        
        s+= "}\n"
        with open("query.rqg", 'w') as fp:
            fp.write(s)

    def generateSparqlGenerateQuery1 (self, deep = False) :
        """generate SPARQL Generate query"""

        s1 = """PREFIX iter: <http://w3id.org/sparql-generate/iter/>
        PREFIX fun: <http://w3id.org/sparql-generate/fn/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        GENERATE {\n"""
        
        s1, s2, dataset = self.recursive_gen_part1(s1, self.dataset, deep=deep)
        
        if (type(dataset)== gpd.GeoDataFrame):
            dataset_path = "./results/data.geojson"
            dataset.to_file(dataset_path, driver="GeoJSON")
        else :
            dataset_path = "./results/data.json"
            dataset.to_json(dataset_path)
        
        s1+=("}} \n SOURCE <{}> AS ?source \nITERATOR iter:GeoJSON(?source) AS ?geometricCoordinates ?properties \n WHERE {{\n".format(dataset_path))

        s1 = s1 + s2
        
        s1+= "}\n"
        with open("query.rqg", 'w') as fp:
            fp.write(s1)

    def split(self, new_class_name:str, class_id:str, predicate:str, class_attributes:list=[], enumerations:list=[]):
        """
        >>> b1=b0.split(new_class_name = 'Commune', class_id='code_com_d', class_attributes = ['code_com_g'],
                predicate='traverseCommuneADroite')
        """

        attributes=[]

        # --- traiter le cas de l'identifiant de la nouvelle classe (clé étrangère pour l'ancienne classe)
        attr_elem = copy.deepcopy(self.get_attribute(class_id))
        attr_elem['id']="oui"
        attributes.append(attr_elem)

        new_dataset = self.dataset[attr_elem['source']].to_frame()

        # --- traiter le cas des autres attributs
        for attr_name in class_attributes:
            if (attr_name != class_id) : # si l'identifiant n'est pas compris dans la liste des attributs (vérification)
                attr_elem = self.get_attribute(attr_name)
                self.attributes.remove(attr_elem) # MAJ du bundle initial
                attributes.append(attr_elem)
                
                new_dataset = new_dataset.join(self.dataset[attr_elem['source']])
                self.dataset.drop(columns=attr_elem['source'], inplace = True) # MAJ du bundle initial

        # --- Créer la nouvelle classe et le lien avec la classe initiale
        new_bundle = BundleClass(new_class_name, new_dataset, attributes= attributes, linked_to=[])
        BundleCollection.add_bundle(self, new_bundle, predicate)

        self.add_link(name = predicate, destination= new_bundle)

        if (enumerations != []) : # si la nvlle classe est liée à des énumérations
            for enum_name in enumerations :
                ass_temp = self.get_link(destination=enum_name)
                self.linked_to.remove(ass_temp) # MAJ du bundle initial

                BundleCollection.graph.remove_edge(self, ass_temp['destination'])
                
                ass_temp['source']= new_bundle # modifier la source
                new_bundle.linked_to.append(ass_temp) # ajouter le lien à la nouvelle classe

                BundleCollection.add_bundle(new_bundle, ass_temp['destination'], ass_temp['name'])
                
                # MAJ datasets
                new_bundle.dataset = new_bundle.dataset.join(self.dataset[ass_temp['destination'].source])                
                self.dataset.drop(columns=ass_temp['destination'].source, inplace = True) # MAJ du bundle initial
 
        return new_bundle

    #---------------------------------- utilities --------------------------------

    def get_id(self) -> dict:
        for attribute_element in self.attributes:
            if attribute_element['id']=="oui":
                return attribute_element
        raise Exception (f"L'identifiant de la classe {self.name} n'est pas précisé dans le modèle sémantique")
    
    def get_attribute(self, name_attribute: str) -> dict:
        for attribute_element in self.attributes:
            if attribute_element["name"]==name_attribute :
                return attribute_element
        raise Exception("L'attribut indiqué n'existe pas")