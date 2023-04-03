import geopandas as gpd
from abc import ABC, abstractmethod
import pandas as pd
import re

URI_PATTERN = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/$"
)

class Bundle(ABC):
    name: str
    IRI: str
    definition: str
    linked_to: list

    dataset: gpd.GeoDataFrame

    instances_namespace = "https://data.grandlyon.com/id/"
    ontology_namespace = "https://data.grandlyon.com/onto/"
    vocabulary_namespace = "https://data.grandlyon.com/vocab/"

    def __init__(
        self,
        name: str,
        dataset: gpd.GeoDataFrame,
        IRI=None,
        definition=None,
        linked_to=[],
    ) -> None:
        self.name = name
        self.dataset = dataset
        self.IRI = IRI
        self.definition = definition
        self.linked_to = linked_to

    def set_instances_namespace(self, namespace: str):
        if URI_PATTERN.fullmatch(namespace):
            self.instances_namespace = namespace
        else:
            raise ValueError("namespace doesn't match a correct URL pattern")

    def set_ontology_namespace(self, namespace: str):
        if URI_PATTERN.fullmatch(namespace):
            self.ontology_namespace = namespace
        else:
            raise ValueError("namespace doesn't match a correct URL pattern")

    def set_vocabulary_namespace(self, namespace: str):
        if URI_PATTERN.fullmatch(namespace):
            self.vocabulary_namespace = namespace
        else:
            raise ValueError("namespace doesn't match a correct URL pattern")

    def show(self):
        """
        show the content of the semantic model
        """
        print("name :", self.name)
        print("IRI :", self.IRI)
        print("definition :", self.definition)

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
        add to the bundle source a link to another bundle destination
        """
        association_element = {}
        association_element["name"] = name
        association_element["IRI"] = IRI
        association_element["definition"] = definition
        association_element["source"] = self
        association_element["destination"] = destination

        self.linked_to.append(association_element)

    def get_link(
        self, name: str = None, source: str = None, destination: str = None
    ) -> dict:
        """
        get the information about a link of the bundle according to its name or its destination
        """
        if name is None and source is None and destination is None:
            raise ValueError("Au moins un paramètre par défaut doit être passé !")
        for association_element in self.linked_to:
            if destination is not None and association_element["destination"].name == destination:
                    return association_element
            elif name is not None and association_element["name"] == name:
                    return association_element
            elif association_element["source"] == source:
                    return association_element
        raise Exception("L'association indiquée n'existe pas")

    @abstractmethod
    def document(self):
        """
        give a definition to an element of the semantic model
        """
        pass

    @abstractmethod
    def annotate(self):
        """
        give an IRI (Internationalized Resource Identifier) to an element of the semantic model
        """
        pass

    @abstractmethod
    def validate(self, errors=[], narrow=True):
        """
        verify the correctness of the semantic model, i.e. a BundleClass must have an IRI or a definition
        """
        pass

    @abstractmethod
    def generateOntology(self, narrow=True, kpi_results=pd.DataFrame()):
        """
        generate a turtle ontology file from the semantic model of the bundle
        """
        pass

    @abstractmethod
    def rename(self):
        """
        rename an element of the semantic model of the bundle
        """
        pass

    # ---------------------------------- dataset utilities --------------------------------
    def show_dataset(self):
        """
        show the content of the dataset
        """
        print(self.dataset)

    # ---------------------------------- utilities --------------------------------

    def index(self, lst: list, key, value):
        """
        get the index of an element in a list of dictionnaries
        """
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        raise Exception

    def write_json(self):
        """
        serialize the semantic model of the bundle in a json file
        """
        raise NotImplementedError()
