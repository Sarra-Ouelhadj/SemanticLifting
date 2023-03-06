from library.read import *
from Bundle import Bundle

def simplify_demo(bundle : Bundle, to_keep: list=['reseau_loc', 'revet_d', 'sens_d']):
    for l in bundle.linked_to[:]:
        if (l['destination'].name not in to_keep and type(l['destination'])== BundleEnum):
            bundle.linked_to.remove(l)
            BundleCollection(bundle)
    return bundle

schema = "https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json"
titre = "AmenagementCyclable"
dataset="./inputs/data_amenagement_cyclable.geojson"

# Part 1

b0=read_jsonSchema_geojsonData(schema,dataset,titre)
simplify_demo(b0)

b0.annotate("http://schema.org/Thing", attributes={"nom_loc":"http://schema.org/name"})

dangling_bundles = b0.children()
dangling_bundles['reseau_loc'].annotate(enum_values={"REV":"http://exemple/REV",
                                                       "Structurant":"http://exemple/Structurant",
                                                       "Autre":"http://exemple/Autre"})
dangling_bundles['revet_d'].annotate(enum_values={"LISSE":"http://exemple/LISSE",
                                                  "RUGUEUX":"http://exemple/RUGUEUX",
                                                  "MEUBLE":"http://exemple/MEUBLE"})
dangling_bundles['sens_d'].document(enum_values={"UNIDIRECTIONNEL":"dans une seule direction", 
                                                 "BIDIRECTIONNEL":"dans les deux directions"})

b0.write_rdf()

# Part 2

b1=b0.split("Commune",'code_com_d','traverse', ['nom_loc','num_iti'], ['sens_d'])
b0.document(associations={'traverse': 'un aménagement qui traverse une commune'})
b1.annotate("http://schema.org/Thing")

b0.write_rdf(deep=True)