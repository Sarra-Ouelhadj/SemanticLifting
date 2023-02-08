from Bundle import Bundle

schema = "https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json"
titre = "AmenagementCyclable"
dataset="https://www.data.gouv.fr/fr/datasets/r/9ca17d67-3ba3-410b-9e32-6ac7948c3e06"

b0=Bundle.read_jsonSchema_geojsonData(schema,dataset,titre)
b0.annotate(attributes={"nom_loc":"http://schema.org/name"},
            class_={"AmenagementCyclable":"http://schema.org/Thing"},
            associations={"aPourreseau_loc":"http://exemple/aPourreseau_loc"},
            enum_values={("reseau_loc_options","REV"):"http://exemple/REV"}
)
#b0.write_rdf()

b1=b0.split(new_class_name = 'Commune', class_id='code_com_d', class_attributes = ['code_com_g'],
        class_association_new_class='traverseCommuneADroite',definition="Division administrative de la Métropole de Lyon",enumerations=['reseau_loc'])

b0.write_rdf("./results/ontology0.ttl","./results/vocabulary0.ttl","./results/instance0.ttl" )
b1.write_rdf("./results/ontology1.ttl","./results/vocabulary1.ttl","./results/instance1.ttl" )
