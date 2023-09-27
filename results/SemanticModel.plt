@startuml
class Station {
	nom_operateur
	{static} id_station_local
	nom_station
	adresse_station
	adresse_rue
	adresse_localite
	adresse_codepostal
	adresse_pays
}
Station --> implantation_station : implantation_station
enum implantation_station {
	Voirie
..
	Parking public
..
	Parking privé à usage public
..
	Parking privé réservé à la clientèle
..
	Station dédiée à la recharge rapide
..
}
@enduml
