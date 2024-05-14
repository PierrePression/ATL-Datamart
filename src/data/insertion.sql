--Script SQL remplissant la table "Ville"
CREATE SEQUENCE ville_id_seq;

ALTER TABLE ville
ALTER COLUMN IDVille SET DEFAULT nextval('ville_id_seq');

INSERT INTO ville (nomVille, codePostal, pays)
values
  ('Paris', 75000, 'France'),
  ('Berlin', 10117, 'Germany'),
  ('Rome', 00187, 'Italy'),
  ('London', '1445184', 'United Kingdom'),
  ('New York City', 10001, 'United States'),
  ('Madrid', 28000, 'Spain'),
  ('Barcelona', 08001, 'Spain'),
  ('Lisbon', 1100001, 'Portugal'),
  ('Amsterdam', 15248, 'Netherlands'),
  ('Brussels', 1000, 'Belgium'),
  ('Vienna', 1010, 'Austria'),
  ('Prague', 11000, 'Czech Republic'),
  ('Copenhagen', 1013, 'Denmark'),
  ('Stockholm', 11152, 'Sweden'),
  ('Helsinki', 00100, 'Finland'),
  ('Warsaw', 00001, 'Poland'),
  ('Budapest', 1013, 'Hungary'),
  ('Bratislava', 81101, 'Slovakia'),
  ('Ljubljana', 1000, 'Slovenia'),
  ('Zagreb', 10000, 'Croatia');


--Script SQL remplissant la table "Mode_Paiement"
CREATE SEQUENCE modePaiement_id_seq;

ALTER TABLE mode_paiement
ALTER COLUMN IDMode_Paiement SET DEFAULT nextval('modePaiement_id_seq');

INSERT INTO mode_paiement (nomModeDePaiement, taxe_ModeDePaiement)
VALUES
  ('Espèces', 0.50),
  ('Carte de crédit', 0.75),
  ('Application de taxi', 1.00),
  ('Bon de taxi', 1.25),
  ('Pass taxi', 1.50);


--Script SQL remplissant la table "Destination"
CREATE SEQUENCE destinations_id_seq;

ALTER TABLE destinations
ALTER COLUMN IDDestination SET DEFAULT nextval('destinations_id_seq');

INSERT INTO destinations (IDVille, IntituleAdresse)
VALUES
  (1, '1600 Pennsylvania Avenue NW, Washington D.C.'),
  (2, 'Brandenburg Gate, Berlin, Germany'),
  (3, 'Colosseum, Rome, Italy'),
  (4, 'Buckingham Palace, London, United Kingdom'),
  (5, 'Times Square, New York City, USA');



--Script SQL remplissant la table "Frais_Trajets"
CREATE SEQUENCE frais_trajets_id_seq;

ALTER TABLE frais_Trajets
ALTER COLUMN IDFraisTrajets SET DEFAULT nextval('frais_trajets_id_seq');

INSERT INTO frais_trajets(
        IDModeDePaiement,  montant_tarif, extra, taxe_MTA, montant_peage, supplement_contribution, frais_embouteillage, frais_aeroport, montant_pourboire, total_prix
    )
    SELECT
        nr.payment_type, nr.fare_amount, nr.extra, nr.mta_tax, nr.tolls_amount, nr.improvement_surcharge, nr.congestion_surcharge, nr.airport_fee, nr.tip_amount, nr.total_amount
    FROM
        nyc_raw nr
    JOIN
    	mode_paiement mp
    ON
    	mp.IDMode_Paiement = nr.payment_type
    JOIN
    	destinations d
    ON
    	d.IDDestination = nr.pulocationid and d.IDDestination = nr.dolocationid
    WHERE (vendorid IS NOT NULL)
    AND (payment_type IS NOT NULL)
    AND (pulocationid IS NOT NULL)
    AND (dolocationid IS NOT NULL)
    AND (passenger_count IS NOT NULL)



 --Script SQL remplissant la table "Trajet"
CREATE SEQUENCE trajets_id_seq;

ALTER TABLE trajet
ALTER COLUMN IDTrajet SET DEFAULT nextval('trajets_id_seq');

  INSERT INTO trajet(
        nombre_passagers, IDdestinationDépart, IDdestinationArrivée, distance, heure_recup, heure_depot, idFrais_Trajets
    )
    SELECT
        nr.passenger_count, nr.pulocationid, nr.dolocationid, nr.trip_distance, nr.tpep_pickup_datetime, nr.tpep_dropoff_datetime, ft.idfraistrajets
    FROM nyc_raw nr
    JOIN frais_trajets ft
    on ft.idmodedepaiement = nr.payment_type and ft.frais_embouteillage = nr.congestion_surcharge
    and ft.montant_tarif = nr.fare_amount and ft.extra = nr.extra and ft.taxe_mta = nr.mta_tax and ft.supplement_contribution = nr.improvement_surcharge and ft.montant_pourboire = nr.tip_amount
    and ft.montant_peage = nr.tolls_amount and ft.frais_aeroport = nr.airport_fee and ft.total_prix = nr.total_amount
    join destinations d
    on d.IDDestination = nr.dolocationid and d.IDDestination = nr.pulocationid
    where
    (payment_type IS NOT NULL)
    AND (pulocationid IS NOT NULL)
    AND (dolocationid IS NOT NULL)
    and (passenger_count is not NULL)


