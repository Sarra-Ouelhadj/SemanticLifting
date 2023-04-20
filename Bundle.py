import geopandas as gpd
from abc import ABC, abstractmethod
import pandas as pd
import re
import reconciler

URI_PATTERN = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/$"
)

RECONCILIATION_SERVICES = {
    "wikidata": {
        "endpoint": "https://wikidata.reconci.link/en/api",
        "namespace": "https://www.wikidata.org/entity/",
    },
    "eol": {
        "endpoint": "https://eol.org/api/reconciliation",
        "namespace": "https://eol.org/",
    },
}


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
        self.reconcilated = False

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
        return rdflib graph of the ontology created
        """
        pass

    @abstractmethod
    def rename(self):
        """
        rename an element of the semantic model of the Bundle
        """
        pass

    def reconcile(
        self,
        name_column_to_reconcile,
        type_id=None,
        top_res: int = 1,
        property_mapping=None,
        reconciliation_endpoint: str = RECONCILIATION_SERVICES["wikidata"]["endpoint"],
        **filter_result
    ):
        """
        reconcile the dataset with various reconciliation services, such as Wikidata.

        Parameters
        ----------
        - name_column_to_reconcile: str
            name of the dataset column
        - type_id: str
            type of items to reconcile against per the API specification (https://www.w3.org/community/reports/reconciliation/CG-FINAL-specs-0.2-20230410/)
            example: type_id="Q515" for http://www.wikidata.org/entity/Q515 for wikidata reconciliation endpoint
        - top_res: int | str
            Either the number of results to return per entry or the string 'all' to return all results
        - property_mapping: dict
            A list of properties to filter results on per the API specification (https://www.w3.org/community/reports/reconciliation/CG-FINAL-specs-0.2-20230410/)
            example for a dataframe (df) about contries reconciled with wikidata : property_mapping={"P17": df["Country"]}
        - reconciliation_endpoint: str, default https://wikidata.reconci.link/en/api
            The reconciliation service to connect to.
        - **filter_result: `match`, `score` or `type_id` keywords to filter the rows of resulting DataFrame
            match : bool
            score : int, i.e. score must be > value
            type_id : str, i.e. the result must be of specified type_id

        Returns
        ---------
        DataFrame of columns:
            id
            description
            match
            name
            score
            type
            type_id
            input_value
        """

        df = reconciler.reconcile(
            column_to_reconcile=self.dataset[name_column_to_reconcile],
            type_id=type_id,
            top_res=top_res,
            property_mapping=property_mapping,
            reconciliation_endpoint=reconciliation_endpoint,
        )

        for key in filter_result:
            if key == "match":
                df = df[df["match"] == filter_result["match"]]
            if key == "score":
                df = df[df["score"] >= filter_result["score"]]
            if key == "type_id":
                df = df[df["type_id"] == filter_result["type_id"]]

        return df

    def make_dictionnary_from_reconcilation_dataFrame(
        self, dataframe: pd.DataFrame, reconciliation_service_name: str = "wikidata"
    ):
        """
        from the reconcile output (DataFrame), make a dictionnary {input_value : IRI}
        """
        dict = {}

        for _, series in dataframe.iterrows():
            dict[series.get("input_value")] = RECONCILIATION_SERVICES[
                reconciliation_service_name
            ]["namespace"] + series.get("id")

        return dict

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
