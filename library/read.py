import requests
import urllib.parse
import json
from BundleClass import BundleClass
from BundleEnum import BundleEnum

# from BundleCollection import BundleCollection
import geopandas as gpd
from library import helpers as h


def read_jsonSchema_geojsonData(
    schema_name: str, dataset_name: str, schema_title: str
) -> BundleClass:
    """
    initialize a first BundleClass with its dangling BundleEnums if enums exist, from a schema developped by schema.data.gouv.fr
    of JSON Schema format and from any GeoJSON dataset compliant with it.

     Parameters
     ----------
     schema_name: relative, absolute path or URL given as a string
        schema to be converted into the semantic model of the bundles created
     dataset_name: relative, absolute path or URL given as a string
        dataset to be loaded into a geopandas.geoDataFrame
     schema_title: str
        title labeling the main concept described in the dataset. Ex: "Cycling facilities"

     Returns
     ---------
     Bundle.BundleClass
        BundleClass root created from the couple (schema, compliant dataset)

    """
    response = urllib.parse.urlsplit(schema_name)
    if response.scheme == "":  # it's a file path
        with open(schema_name, "r") as f:
            schema = json.load(f)
    else:  # it's a URL
        response = requests.get(schema_name)
        schema = response.json()

    dataset = gpd.read_file(dataset_name, rows=100)

    class_name = h.convertToPascalcase(schema_title)
    root_bundle = BundleClass(
        name=class_name, dataset=dataset, attributes=[], linked_to=[]
    )

    id_detected = False

    attributes = schema["properties"]["features"]["items"]["properties"]["properties"][
        "properties"
    ]

    for attr_elem in attributes:
        element_niv1 = {}
        element_niv1["IRI"] = None

        # the "description" field is mandatory
        if "description" in attributes[attr_elem]:
            element_niv1["definition"] = attributes[attr_elem]["description"]
        elif (
            "items" in attributes[attr_elem]
            and "description" in attributes[attr_elem]["items"]
        ):
            element_niv1["definition"] = attributes[attr_elem]["items"]["description"]
        else:
            element_niv1["definition"] = "une définition exemple"

        if "type" in attributes[attr_elem]:  # new adding
            element_niv1["type"] = attributes[attr_elem]["type"]

        if "example" in attributes[attr_elem]:  # new adding
            element_niv1["example"] = attributes[attr_elem]["example"]

        if "pattern" in attributes[attr_elem]:  # new adding
            element_niv1["pattern"] = attributes[attr_elem]["pattern"]

        # new adding
        element_niv1["required"] = (
            "oui"
            if attr_elem
            in schema["properties"]["features"]["items"]["properties"]["properties"][
                "required"
            ]
            else "non"
        )

        element_niv1["name"] = attr_elem

        if "enum" not in attributes[attr_elem]:  # it's an attribute
            element_niv1["id"] = "non"

            if (
                not id_detected
                and attr_elem
                == schema["properties"]["features"]["items"]["properties"][
                    "properties"
                ]["required"][0]
            ):
                element_niv1["id"] = "oui"
                id_detected = True

            root_bundle.attributes.append(element_niv1)

        else:  # it's an enumeration
            new_enum_bundle = BundleEnum(
                attr_elem,
                dataset[attr_elem].to_frame().drop_duplicates(ignore_index=True),
                definition=element_niv1["definition"],
                values=[],
                type=element_niv1["type"],
                required=element_niv1["required"],
            )

            # creating the association between the class and the enumeration type
            root_bundle.add_link(
                attr_elem, new_enum_bundle, None, element_niv1["definition"]
            )

            # enumerated value
            for enum_value in attributes[attr_elem]["enum"]:
                enum_elem = {}
                enum_elem["name"] = enum_value
                enum_elem["definition"] = None
                enum_elem["IRI"] = None
                new_enum_bundle.values.append(enum_elem)

    # BundleCollection(root_bundle)
    return root_bundle


# TODO
def read_template_data(filename: str, dataset_name: str):
    raise NotImplementedError()


def read_tableSchema_csvData(
    schema_name: str,
    dataset_name: str,
    primary_key: str = None,
    schema_title: str = None,
):
    """
    initialize a first BundleClass with its dangling BundleEnums if enums exist, from a schema developped by schema.data.gouv.fr
    of Table Schema format and from any CSV dataset compliant with it.

     Parameters
     ----------
     schema_name: relative, absolute path or URL given as a string
        schema to be converted into the semantic model of the bundles created
     dataset_name: relative, absolute path or URL given as a string
        dataset to be loaded into a geopandas.geoDataFrame
     primary_key: str, optional

     schema_title: str, optional
        title labeling the main concept described in the dataset. Ex: "Cycling facilities"

     Returns
     ---------
     Bundle.BundleClass
        BundleClass root created from the couple (schema, compliant dataset)

    """
    response = urllib.parse.urlsplit(schema_name)

    if response.scheme == "":  # it's a file path
        with open(schema_name, "r") as f:
            schema = json.load(f)
    else:  # it's a URL
        response = requests.get(schema_name)
        schema = response.json()

    dataset = gpd.read_file(dataset_name, rows=100)
    class_name = (
        h.convertToPascalcase(schema["title"])
        if (schema_title is None)
        else h.convertToPascalcase(schema_title)
    )

    if "primaryKey" not in schema and primary_key is None:
        raise Exception(
            "Schema doesn't include a primary key, please indicate one among fields"
        )

    root_bundle = BundleClass(
        name=class_name, dataset=dataset, attributes=[], linked_to=[]
    )

    id_detected = False
    attributes = schema["fields"]
    for attr_elem in attributes:
        element_niv1 = {}
        element_niv1["name"] = attr_elem["name"]
        element_niv1["IRI"] = None
        element_niv1["definition"] = attr_elem["description"]
        element_niv1["type"] = attr_elem["type"]
        element_niv1["example"] = attr_elem["example"]
        element_niv1["required"] = attr_elem["constraints"]["required"]

        if "pattern" in attr_elem["constraints"]:
            element_niv1["pattern"] = attr_elem["constraints"]["pattern"]

        if "enum" not in attr_elem["constraints"]:  # it's an attribute
            if "primaryKey" in schema:
                element_niv1["id"] = "non"

                if not id_detected and attr_elem["name"] == schema["primaryKey"]:
                    element_niv1["id"] = "oui"
                    id_detected = True
            else:
                element_niv1["id"] = "non"

                if not id_detected and attr_elem["name"] == primary_key:
                    element_niv1["id"] = "oui"
                    id_detected = True

            root_bundle.attributes.append(element_niv1)

        else:  # it's an enumeration
            new_enum_bundle = BundleEnum(
                attr_elem["name"],
                dataset[attr_elem["name"]]
                .to_frame()
                .drop_duplicates(ignore_index=True),
                definition=element_niv1["definition"],
                values=[],
                type=element_niv1["type"],
                required=element_niv1["required"],
            )

            # creating the association between the class and the enumeration type
            root_bundle.add_link(
                attr_elem["name"], new_enum_bundle, None, element_niv1["definition"]
            )

            # enumerated value
            for enum_value in attr_elem["constraints"]["enum"]:
                enum_elem = {}
                enum_elem["name"] = enum_value
                enum_elem["definition"] = None
                enum_elem["IRI"] = None
                new_enum_bundle.values.append(enum_elem)

    return root_bundle


# TODO
def read_from_csvData():
    raise NotImplementedError()


# TODO
def read_from_geojsonData():
    raise NotImplementedError()


# TODO
def read_from_jsonData():
    raise NotImplementedError()
