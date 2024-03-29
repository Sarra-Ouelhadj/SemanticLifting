from Bundle import Bundle
from library import helpers as h
from rdflib.namespace import RDF, RDFS, SKOS
from rdflib import Graph, Literal, URIRef, Namespace
import geopandas as gpd
import pandas as pd


class BundleEnum(Bundle):
    values = []
    type: str = ""
    required: str = ""

    def __init__(
        self,
        name: str,
        dataset: gpd.GeoDataFrame,
        IRI=None,
        definition=None,
        values=[],
        type=None,
        required=None,
    ) -> None:
        super().__init__(name, dataset, IRI, definition)
        self.values = values
        self.type = type
        self.required = required

    def show(self):
        """
        show the content of the semantic model
        """
        print("------- Enumeration -------")
        super().show()
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
        rename an element of the semantic model of the BundleEnum
        >>> rename (enumeration_name = "reseau_loc_options")
        >>> rename(enum_values={"REV": "REVETEMENT"})
        """

        if enumeration_name is None and enum_values is None:
            raise ValueError("At least one default parameter must be passed!")

        if enumeration_name is not None:
            self.dataset.rename(columns={self.name: enumeration_name}, inplace=True)
            self.name = enumeration_name

        if enum_values is not None:
            for value in enum_values:
                i = self.index(self.values, "name", value)
                # assign the name
                self.values[i]["name"] = enum_values[value]

        return self

    def annotate(self, enumeration_IRI: str = None, enum_values: dict = None):
        """
        give an IRI (Internationalized Resource Identifier) to an element of the semantic model
        >>> annotate(enumeration_IRI="http://schema.org/Thing")
        >>> annotate(enum_values={"REV":"http://exemple/REV"})
        """

        if enumeration_IRI is None and enum_values is None:
            raise ValueError("At least one default parameter must be passed!")

        if enumeration_IRI is not None:
            self.IRI = enumeration_IRI

        if enum_values is not None:
            for value in enum_values:
                i = self.index(self.values, "name", value)
                # assign IRI
                self.values[i]["IRI"] = enum_values[value]

        return self

    def validate(self):
        """
        verify the correctness of the semantic model

        enumerations validation \n
        0. Chaque énumération doit avoir un nom
        1. Chaque énumération doit avoir un lien de référence ou une définition

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

        if enum_definition is None and enum_values is None:
            raise ValueError("At least one default parameter must be passed!")

        if enum_definition is not None:
            self.definition = enum_definition

        if enum_values is not None:
            for value in enum_values:
                i = self.index(self.values, "name", value)
                # assign a definition
                self.values[i]["definition"] = enum_values[value]

        return self

    def generateOntology(self, vocabulary_graph=Graph(), kpi_results=pd.DataFrame()):
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
            lambda value: value["IRI"] == "" or value["IRI"] is None, self.values
        ):
            valueURI = URIRef(
                self.vocabulary_namespace + h.convertToSnakecase(val["name"])
            )

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

    def reconcile(
        self,
        name_column_to_reconcile=None,
        type_id=None,
        top_res: int = 1,
        property_mapping=None,
        reconciliation_endpoint: str = ...,
        **filter_result,
    ):
        return super().reconcile(
            self.name,
            type_id,
            top_res,
            property_mapping,
            reconciliation_endpoint,
            **filter_result,
        )

    def take_reconcilation_into_account(self, **kwargs):
        """
        for the RDF generation, align IRI of values with the reconcilated IRI of format: {enum_value : IRI}.

        Parameters
        ----------
        **kwargs: variables of type dictionnary for each reconciliation endpoint
            example of variables:
                enpoint1 = {
                    "result": {
                                "UNIDIRECTIONNEL": "http://example1.com/unidirectionnel",
                                "BIDIRECTIONNEL": "http://example1.com/bidirectionnel"
                    },
                    "links":"http://www.w3.org/2004/02/skos/core#exactMatch"
                }
                endpoint2 = {
                    "result": {
                                "UNIDIRECTIONNEL": "http://example2.com/unidirectionnel",
                                "BIDIRECTIONNEL": "http://example2.com/bidirectionnel"
                    },
                    "links":{
                        "UNIDIRECTIONNEL": "http://www.w3.org/2004/02/skos/core#closeMatch",
                        "BIDIRECTIONNEL": "http://www.w3.org/2004/02/skos/core#exactMatch"
                    }
                }
        """
        self.reconcilated = True

        for key in kwargs:
            self.linked_to.append(kwargs[key])

    def _generatePlantUML(self, s):
        """generate PlantUML code from a dictionary"""

        s += ("enum {} {{".format(self.name)) + "\n"
        for value in self.values:
            s += "\t" + value["name"] + "\n..\n"
        s += "}" + "\n"

        return s

    # ---------------------------------- Utilities --------------------------------

    def get_value(self, name_value: str) -> dict:
        """
        get a value of the BundleEnum and its information
        """
        for value_element in self.values:
            if value_element["name"].upper() == name_value.upper():
                return value_element
        raise Exception("La valeur indiquée n'existe pas")
