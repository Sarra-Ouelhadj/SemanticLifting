import copy

# from BundleCollection import BundleCollection
from BundleEnum import BundleEnum
from library import helpers as h
from rdflib.namespace import RDF, RDFS, OWL
from rdflib import Graph, Literal, URIRef, Namespace
from Bundle import Bundle
import geopandas as gpd
import pandas as pd
import urllib.parse

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
    attributes: list = []
    linked_to: list = []

    def __init__(
        self,
        name: str,
        dataset: gpd.GeoDataFrame,
        IRI=None,
        definition=None,
        attributes=[],
        linked_to=[],
    ) -> None:
        super().__init__(name, dataset, IRI, definition)
        self.attributes = attributes
        self.linked_to = linked_to

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
            if deep:
                link_element["destination"].show()
            else:
                print("destination :", link_element["destination"].name)
                print("--------------")

    def children(self) -> dict:
        """
        return the linked bundles in a dictionary of the form: {"name_of_the_bundle": memory_address_of_the_bundle}
        """
        children = {}
        for bun in self.linked_to:
            children[bun["destination"].name] = bun["destination"]
        return children

    def add_link(
        self, name: str, destination: "Bundle", IRI=None, definition: str = None
    ):
        """
        add a link to another bundle
        """
        association_element = {}
        association_element["name"] = name
        association_element["IRI"] = IRI
        association_element["definition"] = definition
        association_element["destination"] = destination

        self.linked_to.append(association_element)

    def get_link(self, name: str = None, destination: str = None) -> dict:
        """
        get the information about a link of the bundle according to its name or its destination
        """
        if name is None and destination is None:
            raise ValueError("At least one default parameter must be passed!")
        for association_element in self.linked_to:
            if (
                destination is not None
                and association_element["destination"].name == destination
            ):
                return association_element
            elif name is not None and association_element["name"] == name:
                return association_element
        raise Exception("The association indicated doesn't exist")

    def rename(
        self, class_name: str = None, attributes: dict = None, associations: dict = None
    ):
        """
        rename an element of the semantic model of the BundleClass
        >>> rename (class_name = "InfrastructureCyclable")
        >>> rename (attributes = {"id_local": "local_identifier"})
        >>> rename (associations = {"reseau_loc": "aPourreseau_loc"})
        """

        if class_name is None and attributes is None and associations is None:
            raise ValueError("At least one default parameter must be passed!")

        if class_name is not None:
            self.name = class_name

        if attributes is not None:
            for value in attributes:
                i = self.index(self.attributes, "name", value)
                # assign the name
                self.attributes[i]["name"] = attributes[value]

            self.dataset.rename(columns=attributes, inplace=True)

        if associations is not None:
            for value in associations:
                i = self.index(self.linked_to, "name", value)
                # assign the name
                self.linked_to[i]["name"] = associations[value]

        return self

    def annotate(
        self, class_IRI: str = None, attributes: dict = None, associations: dict = None
    ):
        """
        give an IRI (Internationalized Resource Identifier) to an element of the semantic model
        >>> annotate(class_IRI="http://schema.org/Thing")
        >>> annotate(attributes={"nom_loc":"http://schema.org/name", "num_iti":"http://schema.org/name"})
        >>> annotate(associations={"reseau_loc":"http://exemple/reseau_loc"})
        """
        if class_IRI is None and attributes is None and associations is None:
            raise ValueError("At least one default parameter must be passed!")

        if class_IRI is not None:
            self.IRI = class_IRI

        if attributes is not None:
            for value in attributes:
                i = self.index(self.attributes, "name", value)
                # assign IRI
                self.attributes[i]["IRI"] = attributes[value]

        if associations is not None:
            for value in associations:
                i = self.index(self.linked_to, "name", value)
                # assign IRI
                self.linked_to[i]["IRI"] = associations[value]

        return self

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

        if class_definition is None and attributes is None and associations is None:
            raise ValueError("At least one default parameter must be passed!")

        if class_definition is not None:
            self.definition = class_definition

        if attributes is not None:
            for value in attributes:
                i = self.index(self.attributes, "name", value)
                # assign a definition
                self.attributes[i]["definition"] = attributes[value]

        if associations is not None:
            for value in associations:
                i = self.index(self.linked_to, "name", value)
                # assign a definition
                self.linked_to[i]["definition"] = associations[value]

        return self

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

        # The total number of classes created
        nb_cl = kpi_results.loc[kpi_results["type"] == "Class", "IRI"].count()
        print("The total number of classes created: ", nb_cl)

        # The total number of DatatypeProperties created
        print(
            "The total number of DatatypeProperties created: ",
            kpi_results.loc[kpi_results["type"] == "DatatypeProperty", "IRI"].count(),
        )

        # The total number of ObjectProperties created
        print(
            "The total number of ObjectProperties created: ",
            kpi_results.loc[kpi_results["type"] == "ObjectProperty", "IRI"].count(),
        )

        # The total number of ConceptSchemes (enumerations) created
        nb_csch = kpi_results.loc[kpi_results["type"] == "ConceptScheme", "IRI"].count()
        print("The total number of ConceptSchemes (enumerations) created: ", nb_csch)

        # The total number of Concepts (enumeration values) created
        print(
            "The total number of Concepts (enumeration values) created: ",
            kpi_results.loc[kpi_results["type"] == "Concept", "IRI"].count(),
        )

        if nb_cl > 1:
            # The number of DatatypeProperties created per class
            print(
                "The number of DatatypeProperties created per class: \n",
                kpi_results.loc[
                    kpi_results["type"] == "DatatypeProperty", ["IRI", "related"]
                ]
                .groupby("related")["IRI"]
                .count()
                .to_frame(),
            )

            # The number of ObjectProperties created per class
            print(
                "The number of ObjectProperties created per class: \n",
                kpi_results.loc[
                    kpi_results["type"] == "ObjectProperty", ["IRI", "related"]
                ]
                .groupby("related")["IRI"]
                .count()
                .to_frame(),
            )

        if nb_csch > 1:
            # The number of Concepts created by ConceptSchemes
            print(
                "The number of Concepts created by ConceptSchemes: \n",
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
        class_id: str,
        class_attributes: list = [],
        enumerations: list = [],
        new_class_name: str = None,
    ):
        """
        divide the BundleClass into 2 new BundleClasses linked to each other
        >>> b1=b0.split(new_class_name = 'Commune', class_id='code_com_d', predicate='traverseCommuneADroite',
                        class_attributes = ['code_com_g'])
        """

        attributes = []
        class_name = class_id if (new_class_name is None) else new_class_name

        # --- treat the new-BundleClass identifier attribute (foreign key of the old class)
        attr_elem = copy.deepcopy(self.get_attribute(class_id))
        attr_elem["id"] = "oui"
        attributes.append(attr_elem)

        new_dataset = self.dataset[attr_elem["name"]].to_frame()

        # --- treat the rest of attributes
        for attr_name in class_attributes:
            if (
                attr_name != class_id
            ):  # if the identifier is not included in the list of attributes
                attr_elem = self.get_attribute(attr_name)
                self.attributes.remove(attr_elem)  # initial BundleClass update
                attributes.append(attr_elem)

                new_dataset = new_dataset.join(self.dataset[attr_elem["name"]])
                self.dataset.drop(
                    columns=attr_elem["name"], inplace=True
                )  # initial BundleClass update

        # --- Create the new BundleClass and the link with the initial BundleClass
        new_bundle = BundleClass(
            class_name, new_dataset, attributes=attributes, linked_to=[]
        )
        # BundleCollection.add_bundle(self, new_bundle, predicate)

        self.add_link(name=class_id, destination=new_bundle)

        if len(enumerations) != 0:  # if the new BundleClass is linked to enumerations
            for enum_name in enumerations:
                ass_temp = self.get_link(destination=enum_name)
                self.linked_to.remove(ass_temp)  # initial BundleClass update

                # BundleCollection.graph.remove_edge(self, ass_temp["destination"])

                new_bundle.linked_to.append(ass_temp)  # add link to new BundleClass

                # BundleCollection.add_bundle(
                #     new_bundle, ass_temp["destination"], ass_temp["name"]
                # )

                # datasets update
                new_bundle.dataset = new_bundle.dataset.join(
                    self.dataset[ass_temp["destination"].name]
                )
                self.dataset.drop(
                    columns=ass_temp["destination"].name, inplace=True
                )  # initial BundleClass update

        return new_bundle

    def generateRDF(self, deep=False, instance_graph=Graph()) -> Graph:
        """
        Return an rdflib graph of a given bundle and it's dangling enumeration bundles
        """
        g = instance_graph
        class_id = self.get_id()["name"]
        for _, series in self.dataset.iterrows():
            s = (
                self.instances_namespace
                + self.name
                + "/"
                + urllib.parse.quote(series.get(class_id))
            )

            for attr in filter(lambda value: value["id"] != "oui", self.attributes):
                p = (
                    self.ontology_namespace + h.convertToCamelcase(attr["name"])
                    if (attr["IRI"] == "" or attr["IRI"] is None)
                    else attr["IRI"]
                )
                o = series.get(attr["name"])
                if pd.notnull(o) and str(o) != '' and not str(o).isspace():
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
                    if pd.notnull(val) and str(val) != '' and not str(val).isspace() :
                        val_temp = link_element["destination"].get_value(val)
                        o = (
                            self.vocabulary_namespace
                            + h.convertToSnakecase(val_temp["name"])
                            if (val_temp["IRI"] == "" or val_temp["IRI"] is None)
                            else val_temp["IRI"]
                        )

                        g.add((URIRef(s), URIRef(p), URIRef(o)))

                        if link_element[
                            "destination"
                        ].reconcilated:  # go down in depth in the graph
                            for item in link_element["destination"].linked_to:
                                if (
                                    val_temp["name"] in item["result"]
                                ):  # if value is reconciliated
                                    if (
                                        type(item["links"]) == str
                                    ):  # same link for all enum values
                                        g.add(
                                            (
                                                URIRef(o),
                                                URIRef(item["links"]),
                                                URIRef(
                                                    item["result"][val_temp["name"]]
                                                ),
                                            )
                                        )
                                    else:  # precise links for each enum value
                                        g.add(
                                            (
                                                URIRef(o),
                                                URIRef(item["links"][val_temp["name"]]),
                                                URIRef(
                                                    item["result"][val_temp["name"]]
                                                ),
                                            )
                                        )

                else:  # it's a class
                    dest_class_id = link_element["destination"].get_id()["name"]
                    val = series.get(dest_class_id)
                    if pd.notnull(val):
                        o = (
                            link_element["destination"].instances_namespace
                            + link_element["destination"].name
                            + "/"
                            + urllib.parse.quote(val)
                        )
                        g.add((URIRef(s), URIRef(p), URIRef(o)))

                    if deep:
                        g = link_element["destination"].generateRDF(True, g)
        return g

    def apply(
        self, func_on_data, columns_types_dic: dict, result_type=None, args=(), **kwargs
    ):
        """
        apply a function (func_on_data) to each row of specfied columns (keys of columns_types_dic dictionnary) of the the dataset,
        and update the semantic model accordingly, i.e. update existing columns type or add new attributes for new columns added
        """
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

    def transform_attribute_to_BundleEnum(self, name_attribute):
        """
        transform an attribute to an enumeration as a BundleEnum
        """
        attribute_element = self.get_attribute(name_attribute)
        dataset_serie = self.dataset[attribute_element["name"]].drop_duplicates()

        # enumeration values
        values = []
        for enum_value in dataset_serie:
            enum_elem = {}
            enum_elem["name"] = enum_value.upper()
            enum_elem["definition"] = None
            enum_elem["IRI"] = None
            values.append(enum_elem)

        new_enum_bundle = BundleEnum(
            attribute_element["name"],
            dataset=dataset_serie.to_frame(),
            definition=attribute_element["definition"],
            linked_to=[],
            values=values,
            type=attribute_element["type"],
            required=attribute_element["required"],
        )

        # add link between the BundleClass and the BundleEnum
        self.add_link(
            attribute_element["name"],
            new_enum_bundle,
            None,
            attribute_element["definition"],
        )
        return new_enum_bundle

    def _generatePlantUML(self, s, deep=False):
        """generate PlantUML code from a dictionary"""

        s += ("class {} {{".format(self.name)) + "\n"

        for attr in self.attributes:
            s += "\t"
            if attr["id"] == "oui":
                s += "{static} "
            s += attr["name"] + "\n"
        s += "}" + "\n"

        for link_element in self.linked_to:
            if type(link_element["destination"]) == BundleEnum:  # it's an enumeration
                s += (
                    "{} --> {} : {}".format(
                        self.name,
                        link_element["destination"].name,
                        link_element["name"],
                    )
                ) + "\n"
                s = link_element["destination"]._generatePlantUML(s)
            else:  # it's a class
                if deep:
                    s += (
                        "{} --> {} : {}".format(
                            self.name,
                            link_element["destination"].name,
                            link_element["name"],
                        )
                    ) + "\n"
                    s = link_element["destination"]._generatePlantUML(s)

        return s

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
        add an attribute to the BundleClass and its information
        """
        attribute_element = {}
        attribute_element["name"] = name
        attribute_element["IRI"] = IRI
        attribute_element["definition"] = definition
        attribute_element["type"] = type
        attribute_element["id"] = "non"
        attribute_element["required"] = required

        self.attributes.append(attribute_element)

    def delete_attribute(self, name_attribute):
        """
        delete an attribute of the BundleClass (not an identifier attribute)
        """
        attribute_element = self.get_attribute(name_attribute)
        if attribute_element["id"] != "oui":
            self.attributes.remove(attribute_element)
        else:
            raise Exception(
                "the attribute is an identifier of the class, please mark another identifier for this class to delete this attribute."
            )
