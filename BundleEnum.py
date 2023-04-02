from Bundle import Bundle
from library import helpers as h
from rdflib.namespace import RDF, RDFS, SKOS
from rdflib import Graph, Literal, URIRef, Namespace
import geopandas as gpd
import pandas as pd


class BundleEnum(Bundle):
    values = []
    source: str = ""
    type: str = ""
    required: str = ""

    def __init__(
        self,
        name: str,
        dataset: gpd.GeoDataFrame,
        IRI=None,
        definition=None,
        linked_to=[],
    ) -> None:
        super().__init__(name, dataset, IRI, definition, linked_to)
        self.values = []
        self.source = None
        self.type = None
        self.required = None

    def show(self):
        """
        show the content of the semantic model
        """
        print("------- Enumeration -------")
        super().show()
        print("source :", self.source)
        print("type :", self.type)
        print("required :", self.required)
        print("\t ------- Values -------")
        for e in self.values:
            print("\t name :", e["name"])
            print("\t definition :", e["definition"])
            print("\t IRI :", e["IRI"])
            print("\t --------------")

    def rename(self, enumeration_name: str = None, enum_values: dict = None):
        """
        rename an element of the semantic model of the bundle
        >>> rename (enumeration_name = "ame_d_options")
        """
        args = locals()
        if any(args.values()) is True:
            if enumeration_name is not None:
                self.name = enumeration_name

            if enum_values is not None:
                enum_keys = list(enum_values.keys())
                for value in enum_keys:
                    i = self.index(self.values, "name", value)
                    # assign the name
                    self.values[i]["name"] = enum_values[value]
        else:
            raise ValueError("At least one default parameter must be passed!")

    def annotate(self, enumeration_IRI: str = None, enum_values: dict = None):
        """
        give an IRI (Internationalized Resource Identifier) to an element of the semantic model
        >>> annotate(enumeration_IRI="http://schema.org/Thing")
        >>> annotate(enum_values={"REV":"http://exemple/REV"})
        """
        args = locals()
        if any(args.values()) is True:
            if enumeration_IRI is not None:
                self.IRI = enumeration_IRI

            if enum_values is not None:
                enum_keys = list(enum_values.keys())
                for value in enum_keys:
                    i = self.index(self.values, "name", value)
                    # affecter l'IRI
                    self.values[i]["IRI"] = enum_values[value]
        else:
            raise ValueError("Au moins un paramètre par défaut doit être passé !")

    def validate(self):
        """
        verify the correctness of the semantic model

        enumerations validation \n
        0. Chaque énumération doit avoir un nom
        1. Chaque énumération doit avoir un lien de référence ou une définition
        2. Chaque énumération doit avoir une source

        enumeration values validation \n
        0. Chaque valeur d'énumération doit avoir un nom
        1. Chaque valeur d'énumération doit avoir un lien de référence ou une définition

        """
        errors = []
        # ------------------------
        # enumeration validation
        # ------------------------

        # 0. L'énumération doit avoir un nom
        if self.name == "" or self.name is None:
            errors.append("Le nom de l'énumération est obligatoire")

        # 1. L'énumération doit avoir un lien de référence ou une définition
        if (self.IRI == "" or self.IRI is None) and (
            self.definition == "" or self.definition is None
        ):
            errors.append(
                f"L'énumération `{self.name}` doit avoir un lien de référence ou une définition"
            )

        # 2. L'énumération doit avoir une source
        if self.source == "" or self.source is None:
            errors.append(f"L'énumération `{self.name}` n'a pas de source")

        # ------------------------
        # enumeration values validation
        # ------------------------
        for enum_val in self.values:
            # 0. Chaque valeur d'énumération doit avoir un nom
            if enum_val["name"] == "" or enum_val["name"] is None:
                errors.append(
                    f"Le nom de la valeur d'énumération `{self.name}` est obligatoire"
                )

            # 1. Chaque valeur d'énumération doit avoir un lien de référence ou une définition
            if (enum_val["IRI"] == "" or enum_val["IRI"] is None) and (
                enum_val["definition"] == "" or enum_val["definition"] is None
            ):
                errors.append(
                    f"La valeur d'énumération `{enum_val['name']}` de l'énumération `{self.name}` doit avoir un lien de référence ou une définition"
                )

        if errors:
            raise Exception(errors)
        else:
            return True

    def _validate(self, errors=[], deep=False):
        """
        return true in the semantic model is correctly filled or a list of errors

        """
        errors = errors
        # ------------------------
        # enumeration validation
        # ------------------------

        # 0. L'énumération doit avoir un nom
        if self.name == "" or self.name is None:
            errors.append("Le nom de l'énumération est obligatoire")

        # 1. L'énumération doit avoir un lien de référence ou une définition
        if (self.IRI == "" or self.IRI is None) and (
            self.definition == "" or self.definition is None
        ):
            errors.append(
                f"L'énumération `{self.name}` doit avoir un lien de référence ou une définition"
            )

        # 2. L'énumération doit avoir une source
        if self.source == "" or self.source is None:
            errors.append(f"L'énumération `{self.name}` n'a pas de source")

        # ------------------------
        # enumeration values validation
        # ------------------------
        for enum_val in self.values:
            # 0. Chaque valeur d'énumération doit avoir un nom
            if enum_val["name"] == "" or enum_val["name"] is None:
                errors.append(
                    f"Le nom de la valeur d'énumération `{self.name}` est obligatoire"
                )

            # 1. Chaque valeur d'énumération doit avoir un lien de référence ou une définition
            if (enum_val["IRI"] == "" or enum_val["IRI"] is None) and (
                enum_val["definition"] == "" or enum_val["definition"] is None
            ):
                errors.append(
                    f"La valeur d'énumération `{enum_val['name']}` de l'énumération `{self.name}` doit avoir un lien de référence ou une définition"
                )

        if not errors:
            return True

    def document(self, enum_definition: str = None, enum_values: dict = None):
        """
        give a definition to an element of the semantic model
        >>> document(enum_values={"UNIDIRECTIONNEL":"dans une seule direction",
                                "BIDIRECTIONNEL":"dans les deux directions"})
        """

        args = locals()
        if any(args.values()) is True:
            if enum_definition is not None:
                self.definition = enum_definition

            if enum_values is not None:
                enum_keys = list(enum_values.keys())
                for value in enum_keys:
                    i = self.index(self.values, "name", value)
                    # donner une définition
                    self.values[i]["definition"] = enum_values[value]
        else:
            raise ValueError("Au moins un paramètre par défaut doit être passé !")

    def generateOntology(self, vocabulary_path: str):
        """generate a turtle ontology file from the semantic model of the bundle"""

        VS = Namespace("http://www.w3.org/2003/06/sw-vocab-status/ns#")
        g2 = Graph()

        enum_created = False
        nb_value_created = 0
        # ------------------------
        # Individuals
        # ------------------------
        if self.IRI is not None and self.IRI != "":
            enumerationURI = URIRef(self.IRI)
        else:
            enumerationURI = URIRef(
                self.vocabulary_namespace + h.convertToPascalcase(self.name)
            )

            self.annotate(enumeration_IRI=str(enumerationURI))

            g2.add((enumerationURI, RDF.type, SKOS.ConceptScheme))
            g2.add((enumerationURI, SKOS.prefLabel, Literal(self.name)))
            g2.add((enumerationURI, SKOS.definition, Literal(self.definition)))
            g2.add(
                (enumerationURI, RDFS.isDefinedBy, URIRef(self.vocabulary_namespace))
            )
            g2.add((enumerationURI, VS.term_status, Literal("testing")))
            enum_created = True

        for val in filter(
            lambda value: False
            if (value["IRI"] != "" and value["IRI"] is not None)
            else True,
            self.values,
        ):
            valueURI = URIRef(
                self.vocabulary_namespace + h.convertToSnakecase(val["name"])
            )

            self.annotate(enum_values={val["name"]: str(valueURI)})

            g2.add((valueURI, RDF.type, SKOS.Concept))
            g2.add((valueURI, SKOS.prefLabel, Literal(val["name"])))
            g2.add((valueURI, SKOS.definition, Literal(val["definition"])))
            g2.add((valueURI, RDFS.isDefinedBy, URIRef(self.vocabulary_namespace)))
            g2.add((valueURI, SKOS.inScheme, enumerationURI))
            g2.add((valueURI, VS.term_status, Literal("testing")))
            nb_value_created += 1

        if enum_created:
            print(f"IRI de l'énumération {self.name} a été créé : {self.IRI}")

        if nb_value_created > 0:
            print(
                f"Le nombre de valeurs créées pour l'énumération `{self.name}` est : {nb_value_created}"
            )

        if enum_created or nb_value_created > 0:
            with open(vocabulary_path, "w") as fv:
                fv.write(g2.serialize(format="turtle"))

    def _generateOntology(self, vocabulary_graph=Graph(), kpi_results=pd.DataFrame()):
        """return rdflib graph of the ontology created"""

        VS = Namespace("http://www.w3.org/2003/06/sw-vocab-status/ns#")
        g2 = vocabulary_graph

        # ------------------------
        # Individuals
        # ------------------------
        if self.IRI is not None and self.IRI != "":
            enumerationURI = URIRef(self.IRI)
        else:
            enumerationURI = URIRef(
                self.vocabulary_namespace + h.convertToPascalcase(self.name)
            )

            self.annotate(enumeration_IRI=str(enumerationURI))

            g2.add((enumerationURI, RDF.type, SKOS.ConceptScheme))
            g2.add((enumerationURI, SKOS.prefLabel, Literal(self.name)))
            g2.add((enumerationURI, SKOS.definition, Literal(self.definition)))
            g2.add(
                (enumerationURI, RDFS.isDefinedBy, URIRef(self.vocabulary_namespace))
            )
            g2.add((enumerationURI, VS.term_status, Literal("testing")))

            df = pd.DataFrame(
                {
                    "IRI": str(enumerationURI),
                    "type": pd.Categorical(["ConceptScheme"]),
                    "related": "NA",
                }
            )

            kpi_results = pd.concat([kpi_results, df], ignore_index=True)

        for val in filter(
            lambda value: False
            if (value["IRI"] != "" and value["IRI"] is not None)
            else True,
            self.values,
        ):
            valueURI = URIRef(
                self.vocabulary_namespace + h.convertToSnakecase(val["name"])
            )

            self.annotate(enum_values={val["name"]: str(valueURI)})

            g2.add((valueURI, RDF.type, SKOS.Concept))
            g2.add((valueURI, SKOS.prefLabel, Literal(val["name"])))
            g2.add((valueURI, SKOS.definition, Literal(val["definition"])))
            g2.add((valueURI, RDFS.isDefinedBy, URIRef(self.vocabulary_namespace)))
            g2.add((valueURI, SKOS.inScheme, enumerationURI))
            g2.add((valueURI, VS.term_status, Literal("testing")))

            df = pd.DataFrame(
                {
                    "IRI": str(valueURI),
                    "type": pd.Categorical(["Concept"]),
                    "related": self.name,
                }
            )

            kpi_results = pd.concat([kpi_results, df], ignore_index=True)

        return g2, kpi_results

    # ---------------------------------- Utilities --------------------------------

    def get_value(self, name_value: str) -> dict:
        """
        get a value of the bundle and its information
        """
        for value_element in self.values:
            if value_element["name"].upper() == name_value.upper():
                return value_element
        raise Exception("La valeur indiquée n'existe pas")
