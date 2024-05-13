-- Création des tables de dimension
CREATE TABLE ville (
    index INT PRIMARY KEY,
    nomVille VARCHAR(255) NOT NULL,
    codePostal INT NOT NULL,
    pays VARCHAR(255) NOT NULL
);

CREATE TABLE mode_paiement (
    IDModeDePaiement INT PRIMARY KEY,
    montant_Pourboire DECIMAL(10,2),
    taxe_MTA DECIMAL(10,2),
    tarif DECIMAL(10,2),
    extra DECIMAL(10,2)
);

CREATE TABLE destinations (
    IDdestination INT PRIMARY KEY,
    IDVille INT NOT NULL,
    IntituleAdresse VARCHAR(255) NOT NULL,
    FOREIGN KEY (IDVille) REFERENCES ville(index)
);

-- Création de la table de faits
CREATE TABLE trajet (
    index INT PRIMARY KEY,
    heure_recup DATE NOT NULL,
    heure_depot DATE NOT NULL,
    distance DECIMAL(10,2) NOT NULL,
    idFrais_Trajets INT NOT NULL,
    nombre_passagers INT NOT NULL,
    FOREIGN KEY (idFrais_Trajets) REFERENCES frais_Trajets(index)
);

-- Création de la table de dimension des frais de trajet
CREATE TABLE frais_Trajets (
    index INT PRIMARY KEY,
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
    FOREIGN KEY (IDModeDePaiement) REFERENCES mode_paiement(IDModeDePaiement)
);