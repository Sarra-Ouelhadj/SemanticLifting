from BundleCollection import BundleCollection
from BundleEnum import BundleEnum
from library.read import read_jsonSchema_geojsonData
from Bundle import Bundle

# from reconciler import reconcile


def simplify_bundle_for_demo(
    bundle: Bundle, to_keep: list = ["reseau_loc", "revet_d", "sens_d"]
):
    """
    simplify the bundle by decreasing the number of BundleEnums to only those mentionned in to_keep list
    """
    bundle.linked_to = [
        lkd for lkd in bundle.linked_to if lkd["destination"].name in to_keep
    ]

    # MAJ du dataset
    rest_of_enums = [
        lkd["destination"].source
        for lkd in bundle.linked_to
        if (
            lkd["destination"].name not in to_keep
            and type(lkd["destination"]) == BundleEnum
        )
    ]
    bundle.dataset.drop(columns=rest_of_enums, inplace=True)

    BundleCollection(
        bundle
    )  # classe statique à modifier pour permettre d'avoir + instances de BundleCollection en cas de manipulation de + JDD en même temps
    return bundle


# schema = "https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json"
schema = "./inputs/schema_amenagements_cyclables.json"
titre = "Amenagement Cyclable"
dataset = "./inputs/data_amenagement_cyclable.geojson"


b0 = read_jsonSchema_geojsonData(schema, dataset, titre)  # initialisation

simplify_bundle_for_demo(b0)  # simplification du schéma pour la démo

# --- Part 1 : annotation, documentation et écriture en RDF d'un seul bundle ---

b0.annotate("http://schema.org/Thing", attributes={"nom_loc": "http://schema.org/name"})

# b0.rename(
#     "InfrastructureCyclable",
#     attributes={"id_local": "local_identifier"},
#     associations={"reseau_loc": "aPourreseau_loc"},
# )

dangling_bundles = b0.children()
# dangling_bundles["reseau_loc"].rename("reseau_loc_options")

# b0.show(True)


dangling_bundles["reseau_loc"].annotate(
    enum_values={
        "REV": "http://exemple/REV",
        "Structurant": "http://exemple/Structurant",
        "Autre": "http://exemple/Autre",
    }
)
dangling_bundles["revet_d"].annotate(
    enum_values={
        "LISSE": "http://exemple/LISSE",
        "RUGUEUX": "http://exemple/RUGUEUX",
        "MEUBLE": "http://exemple/MEUBLE",
    }
)
dangling_bundles["sens_d"].document(
    enum_values={
        "UNIDIRECTIONNEL": "dans une seule direction",
        "BIDIRECTIONNEL": "dans les deux directions",
    }
)

# g = b0.generateRDF(True)

# with open("./results/instances.ttl", "w") as f:
#     f.write(g.serialize(format="turtle"))

# --- Part 2 : split et écriture en RDF d'un ensemble de bundles ---

b1 = b0.split("Commune", "code_com_d", "traverse", ["nom_loc", "num_iti"], ["sens_d"])
b0.document(associations={"traverse": "un aménagement qui traverse une commune"})
b1.annotate("http://schema.org/Thing")

# g = b0.generateRDF(deep=True)

g, kpi = b0.generateOntology(True)
with open("./results/ontology.ttl", "w") as f:
    f.write(g.serialize(format="turtle"))

b0.ontology_kpi(kpi)

# --- Réconciliation : test du package reconciler sur le JDD Aménagements cyclables et Arbres urbains (en cours de travaux)---

# data = b0.dataset.iloc[0:5]

# reconciled = reconcile(data["project_c"], type_id="Q161779")
# print(reconciled)
# reconciled = reconcile(data["source"], type_id="Q7094076")
# print(reconciled)
# reconciled = reconcile(data['code_com_d'], type_id="Q2566253", reconciliation_endpoint = "https://openrefine-reconciliation.linkedopendata.eu/en/api")
# print(reconciled)


# --- Arbres urbains ---
"""
Test de la réconciliation avec le jeu de données des arbres urbains
"""

# dataset = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=abr_arbres_alignement.abrarbre&outputFormat=application/json;%20subtype=geojson&SRSNAME=EPSG:4171"
# df = gpd.read_file(dataset, rows = 10) # chargement d'une partie du fichier

# EOL_RECONCILIATION_ENDPOINT = "https://eol.org/api/reconciliation"

# reconciled = reconcile(df['essence'], type_id="taxon", reconciliation_endpoint=EOL_RECONCILIATION_ENDPOINT)
# print(reconciled)
