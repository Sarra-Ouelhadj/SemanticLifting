from Bundle import Bundle
from BundleCollection import BundleCollection
from library.read import *

schema = "https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json"
titre = "Amenagement Cyclable"
#dataset="https://www.data.gouv.fr/fr/datasets/r/9ca17d67-3ba3-410b-9e32-6ac7948c3e06"
dataset="./inputs/data_amenagement_cyclable.geojson"


b0=read_jsonSchema_geojsonData(schema,dataset,titre)

f=b0[0].split('Commune', 'code_com_d', ['code_com_g'],predicate='traverseCommuneADroite', enumerations=['reseau_loc'])
b0[0].show_dataset()
f.show_dataset()
#dataset = self.dataset.merge(bun.dataset, left_on=self.semantic_model.get_id()['source'], right_on=bun.semantic_model.get_id()['source'])



#BundleCollection.show()

#b0[0].generateSparqlGenerateQuery()

#b0.semantic_model.write_json("./results/semantic_model0.json")
# b0.annotate(attributes={"nom_loc":"http://schema.org/name"},
#             class_={"AmenagementCyclable":"http://schema.org/Thing"},
#             associations={"reseau_loc":"http://exemple/reseau_loc"},
#             enum_values={("reseau_loc","REV"):"http://exemple/REV"}
# )
#print(b0.semantic_model.get_association())
#b0.semantic_model.generateOntology("./results/ontologyX.ttl","./results/vocabularyX.ttl",b0.ontology_namespace, b0.vocabulary_namespace)

#b0.write_rdf("./results/instanceX.ttl")

# b1=b0.split(new_class_name = 'Commune', class_id='code_com_d', class_attributes = ['code_com_g'],
#         predicate='traverseCommuneADroite',enumerations=['reseau_loc'])



#BundleCollection.show()

#b1.semantic_model.write_json("./results/semantic_model1.json")

#b0.write_rdf("./results/ontology0.ttl","./results/vocabulary0.ttl","./results/instance0.ttl" )
#b1.write_rdf("./results/ontology1.ttl","./results/vocabulary1.ttl","./results/instance1.ttl" )
