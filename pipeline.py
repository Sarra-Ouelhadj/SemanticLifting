from library.read import *
from Bundle import Bundle

schema = "https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json"
titre = "Amenagement Cyclable"
dataset="./inputs/data_amenagement_cyclable.geojson"


b0=read_jsonSchema_geojsonData(schema,dataset,titre)

#b0.show()
#BundleCollection.show()


# dagling_bundles = b0.next()

# dagling_bundles['revet_g'].show()

# dagling_bundles['revet_g'].annotate(enumeration_IRI="http://schema.org/Thing", enum_values={"LISSE":"http://exemple/LISSE"} )

# dagling_bundles['revet_g'].show()

b1=b0.split("Commune",'code_com_d','traverse', ['nom_loc','num_iti'], ['ame_d', 'regime_d'])

#BundleCollection.show()


# b1.show()

# b1.document("Division administrative de la Métropole de Lyon")
b0.annotate("http://schema.org/Thing")
b0.document(associations={'traverse': 'un aménagement qui traverse une commune'})

# b1.show()

b0.generateOntology("./results/oo.ttl")

b0.write_rdf()

Bundle.insert()