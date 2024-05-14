-- Création des tables des villes
CREATE TABLE ville (
    IDVille INT PRIMARY KEY,
    nomVille VARCHAR(255) NOT NULL,
    codePostal INT NOT NULL,
    pays VARCHAR(255) NOT NULL
);


-- Création de la table des modes de paiement
CREATE TABLE mode_paiement (
    IDMode_Paiement INT PRIMARY KEY,
    nomModeDePaiement VARCHAR(255),
    taxe_ModeDePaiement DECIMAL(10,2)
);


-- Création de la table des destinations
CREATE TABLE destinations (
    IDDestination INT PRIMARY KEY,
    IDVille INT NOT NULL,
    IntituleAdresse VARCHAR(255) NOT NULL,
    FOREIGN KEY (IDVille) REFERENCES ville(IDVille)
);

-- Création de la table des frais de trajet
CREATE TABLE frais_Trajets (
    IDFraisTrajets INT PRIMARY KEY,
    IDdestinationArrivée INT NOT NULL,
    IDdestinationDépart INT NOT NULL,
    frais_embouteillage DECIMAL(10,2),
    montant_tarif DECIMAL(10,2),
    extra DECIMAL(10,2),
    taxe_MTA DECIMAL(10,2),
    supplement_contribution DECIMAL(10,2),
    montant_pourboire DECIMAL(10,2),
    IDModeDePaiement INT NOT NULL,
    montant_peage DECIMAL(10,2),
    frais_aeroport DECIMAL(10,2),
    total_prix DECIMAL(10,2),

    FOREIGN KEY (IDdestinationArrivée) REFERENCES destinations(IDdestination),
    FOREIGN KEY (IDdestinationDépart) REFERENCES destinations(IDdestination),
    FOREIGN KEY (IDModeDePaiement) REFERENCES mode_paiement(IDMode_Paiement)
);

-- Création de la table des trajets
CREATE TABLE trajet (
    IDTrajet INT PRIMARY KEY,
    heure_recup DATE NOT NULL,
    heure_depot DATE NOT NULL,
    distance DECIMAL(10,2) NOT NULL,
    idFrais_Trajets INT NOT NULL,
    nombre_passagers INT NOT NULL,
    FOREIGN KEY (idFrais_Trajets) REFERENCES frais_Trajets(IDFraisTrajets)
);


