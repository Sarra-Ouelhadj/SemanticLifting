import copy
from BundleCollection import BundleCollection
from BundleEnum import BundleEnum
from library import helpers as h
from rdflib.namespace import RDF, RDFS, OWL
from rdflib import Graph, Literal, URIRef, Namespace
from Bundle import Bundle
import geopandas as gpd
import pandas as pd

PANDAS_JSONSCHEMA_TYPES_MATCHING = {
    "object": "string",
    "int64": "integer",
    "float64": "number",
    "bool": "boolean",
    "datetime64": "string",
    "timedelta[ns]": "string",
    "category": "string",
}


class BundleClass(Bundle):
    attributes = []

    def __init__(
        self,
        name: str,
        dataset: gpd.GeoDataFrame,
        IRI=None,
        definition=None,
        attributes=[],
        linked_to=[],
    ) -> None:
        super().__init__(name, dataset, IRI, definition, linked_to)
        self.attributes = attributes

    def show(self, deep=False):
        """
        show the content of the semantic model
        """
        print("------- Class -------")
        super().show()
        print("\t ------- attributes -------")
        for attr in self.attributes:
            print("\t name :", attr["name"])
            print("\t IRI :", attr["IRI"])
            print("\t definition :", attr["definition"])
            print("\t type :", attr["type"])
            print("\t id :", attr["id"])
            print("\t required :", attr["required"])
            print("\t --------------")
        if self.linked_to:
            print("------- Links -------")
        for link_element in self.linked_to:
            print("name :", link_element["name"])
            print("IRI :", link_element["IRI"])
            print("definition :", link_element["definition"])
            print("source :", link_element["source"])
            if deep:
                link_element["destination"].show()
            else:
                print("destination :", link_element["destination"].name)
                print("--------------")

    def rename(
        self, class_name: str = None, attributes: dict = None, associations: dict = None
    ):
        """
        rename an element of the semantic model of the bundle
        >>> rename (class_name = "InfrastructureCyclable")
        >>> rename (attributes = {"id_local": "local_identifier"})
        >>> rename (associations = {"reseau_loc": "aPourreseau_loc"})
        """
        args = locals()
        if any(args.values()):
            if class_name is not None:
                self.name = class_name

            if attributes is not None:
                attributes_keys = list(attributes.keys())
                for value in attributes_keys:
                    i = self.index(self.attributes, "name", value)
                    # assign the name
                    self.attributes[i]["name"] = attributes[value]

            if associations is not None:
                associations_keys = list(associations.keys())
                for value in associations_keys:
                    i = self.index(self.linked_to, "name", value)
                    # assign the name
                    self.linked_to[i]["name"] = associations[value]
            return self
        else:
            raise ValueError("At least one default parameter must be passed!")

    def annotate(
        self, class_IRI: str = None, attributes: dict = None, associations: dict = None
    ):
        """
        give an IRI (Internationalized Resource Identifier) to an element of the semantic model
        >>> annotate(class_IRI="http://schema.org/Thing")
        >>> annotate(attributes={"nom_loc":"http://schema.org/name", "num_iti":"http://schema.org/name"})
        >>> annotate(associations={"reseau_loc":"http://exemple/reseau_loc"})
        """
        args = locals()
        if any(args.values()) is True:
            if class_IRI is not None:
                self.IRI = class_IRI

            if attributes is not None:
                attributes_keys = list(attributes.keys())
                for value in attributes_keys:
                    i = self.index(self.attributes, "name", value)
                    # affecter l'IRI
                    self.attributes[i]["IRI"] = attributes[value]

            if associations is not None:
                associations_keys = list(associations.keys())
                for value in associations_keys:
                    i = self.index(self.linked_to, "name", value)
                    # affecter l'IRI
                    self.linked_to[i]["IRI"] = associations[value]
            return self
        else:
            raise ValueError("At least one default parameter must be passed!")

    def validate(self, errors=[], deep=False):
        """
        verify the correctness of the semantic model

        class validation \n
        0. La classe doit avoir un nom
        1. La classe doit avoir un lien de référence ou une définition

        attributes validation \n
        0. Chaque attribut doit avoir un nom
        1. Chaque attribut doit avoir un lien de référence ou une définition
        2. Le champs identifiant n'est pas vide
        3. Chaque classe doit avoir au minimum un identifiant
        4. Pas d'attributs avec le même nom dans le modèle sémantique

        associations validation \n
        0. Chaque association doit avoir un nom
        1. Chaque association doit avoir un lien de référence ou une définition
        2. Chaque association doit avoir une source
        3. Chaque association doit avoir une destination
        """
        errors = errors

        # ------------------------
        # classe validation
        # ------------------------

        # 0. La classe doit avoir un nom
        if self.name == "" or self.name is None:
            errors.append("Le nom de la classe est obligatoire")

        # 1. La classe doit avoir un lien de référence ou une définition
        if (self.IRI == "" or self.IRI is None) and (
            self.definition == "" or self.definition is None
        ):
            errors.append(
                f"La classe `{self.name}` doit avoir un lien de référence ou une définition"
            )

        # ------------------------
        # attributes validation
        # ------------------------

        attribute_total_number = 0
        set_of_attributes = set()
        list = []

        for attr in self.attributes:
            # 0. Chaque attribut doit avoir un nom
            if attr["name"] == "" or attr["name"] is None:
                errors.append("Le nom de l'attribut est obligatoire")

            # 1. Chaque attribut doit avoir un lien de référence ou une définition
            if (attr["IRI"] == "" or attr["IRI"] is None) and (
                attr["definition"] == "" or attr["definition"] is None
            ):
                errors.append(
                    f"L'attribut `{attr['name']}` doit avoir un lien de référence ou une définition"
                )

            # 3. Le champs identifiant n'est pas vide
            if attr["id"] == "" or attr["id"] is None:
                errors.append(
                    f"Le champs 'Identifiant' n'est pas précisé pour l'attribut `{attr['name']}`"
                )

            list.append(attr["id"])
            attribute_total_number += 1
            set_of_attributes.add(attr["name"])

        # 4. La classe doit avoir au minimum un identifiant
        if "oui" not in list:
            errors.append(f"la classe `{self.name}` n'a pas d'identifiant")

        # 5. Pas d'attributs avec le même nom dans le modèle sémantique
        if len(set_of_attributes) < attribute_total_number:
            errors.append(
                "Des attributs de même nom existent dans le modèle sémantique"
            )

        # ------------------------
        # associations validation
        # ------------------------

        for ass in self.linked_to:
            # 0. Chaque association doit avoir un nom
            if ass["name"] == "" or ass["name"] is None:
                errors.append("Le nom de l'association est obligatoire")

            # 1. Chaque association doit avoir un lien de référence ou une définition
            if (ass["IRI"] == "" or ass["IRI"] is None) and (
                ass["definition"] == "" or ass["definition"] is None
            ):
                errors.append(
                    f"L'association `{ass['name']}` doit avoir un lien de référence ou une définition"
                )

            # 2. Chaque association doit avoir une source
            if ass["source"] == "" or ass["source"] is None:
                errors.append(f"L'association `{ass['name']}` doit avoir une source")

            # 3. Chaque association doit avoir une destination
            if ass["destination"] == "" or ass["destination"] is None:
                errors.append(
                    f"L'association `{ass['name']}` doit avoir une destination"
                )

            if type(ass["destination"]) == type(self):
                if deep:
                    ass["destination"].validate(errors, deep)
            else:
                ass["destination"]._validate(errors, deep)

        try:
            if errors:
                raise Exception(errors)
            else:
                return True
        except Exception as e:
            raise e

    def document(
        self,
        class_definition: str = None,
        attributes: dict = None,
        associations: dict = None,
    ):
        """
        give a definition to an element of the semantic model
        >>> document(associations = {'aPourProfession' : 'La profession de la personne'})
        """
        args = locals()
        if any(args.values()):
            if class_definition is not None:
                self.definition = class_definition

            if attributes is not None:
                attributes_keys = list(attributes.keys())
                for value in attributes_keys:
                    i = self.index(self.attributes, "name", value)
                    # donner une définition
                    self.attributes[i]["definition"] = attributes[value]

            if associations is not None:
                associations_keys = list(associations.keys())
                for value in associations_keys:
                    i = self.index(self.linked_to, "name", value)
                    # donner une définition
                    self.linked_to[i]["definition"] = associations[value]
            return self
        else:
            raise ValueError("Au moins un paramètre par défaut doit être passé !")

    def mark_identifier(self, name_attribute: str):
        """
        mark an attribute as an identifier of the BundleClass
        """

        # mark the attribute as an identifier
        attr_element = self.get_attribute(name_attribute)
        attr_element["id"] = "oui"

        # turn the previous identifier to a simple attribute
        attr_element = self.get_id()
        attr_element["id"] = "non"

        return self

    def ontology_kpi(self, kpi_results: pd.DataFrame):
        """
         generate some KPIs on the generated ontology: \n
        - number of classes
        - number of DatatypeProperties created
        - number of ObjectProperties created
        - number of ConceptSchemes created
        - number of Concepts created
        - number of DatatypeProperties create per class if multiple classes created
        - number of ObjectProperties created per class if multiple classes created
        - number of Concepts created per ConceptScheme if multiple ConceptSchemes created

        """

        # Le nombre de classes créées au total
        nb_cl = kpi_results.loc[kpi_results["type"] == "Class", "IRI"].count()
        print("Le nombre de classes créées au total : ", nb_cl)

        # Le nombre de DatatypeProperties créées au total
        print(
            "Le nombre de DatatypeProperties créées au total : ",
            kpi_results.loc[kpi_results["type"] == "DatatypeProperty", "IRI"].count(),
        )

        # Le nombre d'ObjectProperties créés au total
        print(
            "Le nombre d'ObjectProperties créés au total : ",
            kpi_results.loc[kpi_results["type"] == "ObjectProperty", "IRI"].count(),
        )

        # Le nombre de ConceptSchemes (énumérations) créés au total
        nb_csch = kpi_results.loc[kpi_results["type"] == "ConceptScheme", "IRI"].count()
        print("Le nombre de ConceptSchemes (énumérations) créés au total : ", nb_csch)

        # Le nombre de Concepts (valeurs d'énumération) créés au total
        print(
            "Le nombre de Concepts (valeurs d'énumération) créés au total : ",
            kpi_results.loc[kpi_results["type"] == "Concept", "IRI"].count(),
        )

        if nb_cl > 1:
            # Le nombre de DatatypeProperties créées par classe
            print(
                "Le nombre de DatatypeProperties créées par classe : \n",
                kpi_results.loc[
                    kpi_results["type"] == "DatatypeProperty", ["IRI", "related"]
                ]
                .groupby("related")["IRI"]
                .count()
                .to_frame(),
            )

            # Le nombre d'ObjectProperties créés par classe
            print(
                "Le nombre d'ObjectProperties créés par classe : \n",
                kpi_results.loc[
                    kpi_results["type"] == "ObjectProperty", ["IRI", "related"]
                ]
                .groupby("related")["IRI"]
                .count()
                .to_frame(),
            )

        if nb_csch > 1:
            # Le nombre de Concepts créés par ConceptSchemes
            print(
                "Le nombre de Concepts créés par ConceptSchemes : \n",
                kpi_results.loc[kpi_results["type"] == "Concept", ["IRI", "related"]]
                .groupby("related")["IRI"]
                .count()
                .to_frame(),
            )

    def generateOntology(
        self,
        deep=False,
        ontology_graph=Graph(),
        kpi_results=pd.DataFrame(),
    ):
        """
        return rdflib graph of the ontology created
        """

        VS = Namespace("http://www.w3.org/2003/06/sw-vocab-status/ns#")
        g = ontology_graph

        # ------------------------
        # Classes
        # ------------------------
        if self.IRI == "" or self.IRI is None:
            classeURI = URIRef(
                self.ontology_namespace + h.convertToPascalcase(self.name)
            )

            # self.annotate(class_IRI=str(classeURI))

            g.add((classeURI, RDF.type, OWL.Class))
            g.add((classeURI, RDFS.label, Literal(self.name)))
            g.add((classeURI, RDFS.comment, Literal(self.definition)))
            g.add((classeURI, RDFS.isDefinedBy, URIRef(self.ontology_namespace)))
            g.add((classeURI, VS.term_status, Literal("testing")))

            df = pd.DataFrame(
                {
                    "IRI": str(classeURI),
                    "type": pd.Categorical(["Class"]),
                    "related": "NA",
                }
            )

            kpi_results = pd.concat([kpi_results, df], ignore_index=True)

        # ------------------------
        # Data Properties
        # ------------------------
        for attr in filter(
            lambda value: value["IRI"] == "" or value["IRI"] is None,
            self.attributes,
        ):
            attributeURI = URIRef(
                self.ontology_namespace + h.convertToCamelcase(attr["name"])
            )

            # self.annotate(attributes={attr["name"]: str(attributeURI)})

            g.add((attributeURI, RDF.type, OWL.DatatypeProperty))
            g.add((attributeURI, RDFS.label, Literal(attr["name"])))
            g.add((attributeURI, RDFS.comment, Literal(attr["definition"])))
            g.add((attributeURI, RDFS.isDefinedBy, URIRef(self.ontology_namespace)))
            g.add((attributeURI, VS.term_status, Literal("testing")))

            df = pd.DataFrame(
                {
                    "IRI": str(attributeURI),
                    "type": pd.Categorical(["DatatypeProperty"]),
                    "related": self.name,
                }
            )

            kpi_results = pd.concat([kpi_results, df], ignore_index=True)

        # ------------------------
        # Object Properties
        # ------------------------
        for ass in filter(
            lambda value: value["IRI"] == "" or value["IRI"] is None,
            self.linked_to,
        ):
            associationURI = URIRef(
                self.ontology_namespace + h.convertToCamelcase(ass["name"])
            )

            # self.annotate(associations={ass["name"]: str(associationURI)})

            g.add((associationURI, RDF.type, OWL.ObjectProperty))
            g.add((associationURI, RDFS.label, Literal(ass["name"])))
            g.add((associationURI, RDFS.comment, Literal(ass["definition"])))
            g.add((associationURI, RDFS.isDefinedBy, URIRef(self.ontology_namespace)))
            g.add((associationURI, VS.term_status, Literal("testing")))

            df = pd.DataFrame(
                {
                    "IRI": str(associationURI),
                    "type": pd.Categorical(["ObjectProperty"]),
                    "related": self.name,
                }
            )

            kpi_results = pd.concat([kpi_results, df], ignore_index=True)

            if type(ass["destination"]) == BundleClass:
                if deep:
                    g, kpi_results = ass["destination"].generateOntology(
                        deep, g, kpi_results
                    )
            else:
                g, kpi_results = ass["destination"].generateOntology(g, kpi_results)

        return g, kpi_results

    def split(
        self,
        new_class_name: str,
        class_id: str,
        predicate: str,
        class_attributes: list = [],
        enumerations: list = [],
    ):
        """
        divide a bundle into 2 new bundles linked to each other
        >>> b1=b0.split(new_class_name = 'Commune', class_id='code_com_d', predicate='traverseCommuneADroite',
                        class_attributes = ['code_com_g'])
        """

        attributes = []

        # --- traiter le cas de l'identifiant de la nouvelle classe (clé étrangère pour l'ancienne classe)
        attr_elem = copy.deepcopy(self.get_attribute(class_id))
        attr_elem["id"] = "oui"
        attributes.append(attr_elem)

        new_dataset = self.dataset[attr_elem["name"]].to_frame()

        # --- traiter le cas des autres attributs
        for attr_name in class_attributes:
            if (
                attr_name != class_id
            ):  # si l'identifiant n'est pas compris dans la liste des attributs (vérification)
                attr_elem = self.get_attribute(attr_name)
                self.attributes.remove(attr_elem)  # MAJ du bundle initial
                attributes.append(attr_elem)

                new_dataset = new_dataset.join(self.dataset[attr_elem["name"]])
                self.dataset.drop(
                    columns=attr_elem["name"], inplace=True
                )  # MAJ du bundle initial

        # --- Créer la nouvelle classe et le lien avec la classe initiale
        new_bundle = BundleClass(
            new_class_name, new_dataset, attributes=attributes, linked_to=[]
        )
        BundleCollection.add_bundle(self, new_bundle, predicate)

        self.add_link(name=predicate, destination=new_bundle)

        if len(enumerations) != 0:  # si la nvlle classe est liée à des énumérations
            for enum_name in enumerations:
                ass_temp = self.get_link(destination=enum_name)
                self.linked_to.remove(ass_temp)  # MAJ du bundle initial

                BundleCollection.graph.remove_edge(self, ass_temp["destination"])

                ass_temp["source"] = new_bundle  # modifier la source
                new_bundle.linked_to.append(
                    ass_temp
                )  # ajouter le lien à la nouvelle classe

                BundleCollection.add_bundle(
                    new_bundle, ass_temp["destination"], ass_temp["name"]
                )

                # MAJ datasets
                new_bundle.dataset = new_bundle.dataset.join(
                    self.dataset[ass_temp["destination"].name]
                )
                self.dataset.drop(
                    columns=ass_temp["destination"].name, inplace=True
                )  # MAJ du bundle initial

        return new_bundle

    def generateRDF(self, deep=False, instance_graph=Graph()) -> Graph:
        """
        Return an rdflib graph of a given bundle and it's dangling enumeration bundles
        """
        g = instance_graph
        class_id = self.get_id()["name"]
        for _, series in self.dataset.iterrows():
            s = self.instances_namespace + self.name + "/" + series.get(class_id)

            for attr in filter(lambda value: value["id"] != "oui", self.attributes):
                p = (
                    self.ontology_namespace + h.convertToCamelcase(attr["name"])
                    if (attr["IRI"] == "" or attr["IRI"] is None)
                    else attr["IRI"]
                )
                o = series.get(attr["name"])
                if pd.notnull(o):
                    g.add((URIRef(s), URIRef(p), Literal(o)))

            for link_element in self.linked_to:
                p = (
                    self.ontology_namespace + h.convertToCamelcase(link_element["name"])
                    if (link_element["IRI"] == "" or link_element["IRI"] is None)
                    else link_element["IRI"]
                )

                if (
                    type(link_element["destination"]) == BundleEnum
                ):  # it's an enumeration
                    val = series.get(link_element["destination"].name)
                    if pd.notnull(val):
                        val_temp = link_element["destination"].get_value(val)
                        o = (
                            self.vocabulary_namespace
                            + h.convertToSnakecase(val_temp["name"])
                            if (val_temp["IRI"] == "" or val_temp["IRI"] is None)
                            else val_temp["IRI"]
                        )

                        g.add((URIRef(s), URIRef(p), URIRef(o)))

                else:  # it's a class
                    dest_class_id = link_element["destination"].get_id()["name"]
                    val = series.get(dest_class_id)
                    if pd.notnull(val):
                        o = (
                            link_element["destination"].instances_namespace
                            + link_element["destination"].name
                            + "/"
                            + val
                        )
                        g.add((URIRef(s), URIRef(p), URIRef(o)))

                    if deep:
                        g = link_element["destination"].generateRDF(True, g)
        return g

    def apply(
        self, func_on_data, columns_types_dic: dict, result_type=None, args=(), **kwargs
    ):
        columns = self.dataset.columns
        self.dataset[[*columns_types_dic]] = self.dataset.apply(
            func_on_data,
            axis=1,
            raw=False,
            result_type=result_type,
            args=args,
            **kwargs,
        )

        for col, type in columns_types_dic.items():
            if col in columns:  # existing column updated
                attr_elem = self.get_attribute(col)
                attr_elem["type"] = type

            else:  # new column created
                self.add_attribute(col, type=type)

        return self

    # ---------------------------------- Utilities --------------------------------

    def get_id(self) -> dict:
        """
        get the identifier of the BundleClass and its information
        """
        for attribute_element in self.attributes:
            if attribute_element["id"] == "oui":
                return attribute_element
        raise Exception(
            f"L'identifiant de la classe {self.name} n'est pas précisé dans le modèle sémantique"
        )

    def get_attribute(self, name_attribute: str) -> dict:
        """
        get an attribute of the BundleClass and its information
        """
        for attribute_element in self.attributes:
            if attribute_element["name"] == name_attribute:
                return attribute_element
        raise Exception("L'attribut indiqué n'existe pas")

    def add_attribute(
        self,
        name: str,
        IRI=None,
        definition: str = None,
        type: str = "string",
        required: str = "non",
    ):
        """
        add an attribute to the bundle
        """
        attribute_element = {}
        attribute_element["name"] = name
        attribute_element["IRI"] = IRI
        attribute_element["definition"] = definition
        attribute_element["type"] = type
        attribute_element["required"] = required

        self.attributes.append(attribute_element)
