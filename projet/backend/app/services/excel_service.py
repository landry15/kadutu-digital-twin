import os
import re
import unicodedata

import pandas as pd
from sqlalchemy import text

from app.database.connection import engine


# ============================================================
# CONFIGURATION
# ============================================================

EXCEL_PATH = os.path.join(
    "data",
    "reseau_kadutu.xlsx"
)

FEUILLES_ATTENDUES = [
    "NOEUDS",
    "CONDUITES",
    "POINTS_CONDUITES",
    "RÉSERVOIRS",
    "VANNES",
    "BORNES_FONTAINES"
]


# ============================================================
# NORMALISATION DES NOMS
# ============================================================

def normaliser_nom(nom):
    """
    Normalise un nom de colonne ou de feuille.

    Exemples :
        NODE_ID       -> node_id
        node_id       -> node_id
        Node Id       -> node_id
        LATITUDE      -> latitude
        Latitude      -> latitude
        NŒUD_DEPART   -> noeud_depart
        Nœud Départ   -> noeud_depart
    """

    nom = str(nom).strip()

    # Suppression des accents
    nom = unicodedata.normalize(
        "NFKD",
        nom
    ).encode(
        "ascii",
        "ignore"
    ).decode(
        "ascii"
    )

    # Minuscules
    nom = nom.lower()

    # Espaces et caractères spéciaux
    # deviennent des underscores
    nom = re.sub(
        r"[^a-z0-9]+",
        "_",
        nom
    )

    # Supprimer les underscores inutiles
    nom = nom.strip("_")

    return nom


# ============================================================
# NORMALISATION DES COLONNES
# ============================================================

def normaliser_colonnes(df):
    """
    Normalise automatiquement les noms des colonnes Excel.
    """

    nouvelles_colonnes = []

    for colonne in df.columns:

        colonne_normalisee = normaliser_nom(
            colonne
        )

        # Variantes particulières
        if colonne_normalisee == "noeud_arrive":
            colonne_normalisee = "noeud_arrivee"

        nouvelles_colonnes.append(
            colonne_normalisee
        )

    df.columns = nouvelles_colonnes

    return df


# ============================================================
# RECHERCHE D'UNE FEUILLE
# ============================================================

def trouver_feuille(feuilles, recherche):
    """
    Recherche une feuille Excel sans tenir compte :
    - des majuscules ;
    - des minuscules ;
    - des accents ;
    - des espaces.
    """

    recherche_normalisee = normaliser_nom(
        recherche
    )

    for feuille in feuilles:

        if normaliser_nom(
            feuille
        ) == recherche_normalisee:

            return feuille

    return None


# ============================================================
# LECTURE DU FICHIER EXCEL
# ============================================================

def lire_excel():

    if not os.path.exists(EXCEL_PATH):

        raise FileNotFoundError(
            f"Fichier Excel introuvable : "
            f"{EXCEL_PATH}"
        )

    fichier = pd.ExcelFile(
        EXCEL_PATH
    )

    print("\n========================================")
    print("     LECTURE DU FICHIER EXCEL")
    print("========================================")

    print("\nFeuilles trouvées :")

    for feuille in fichier.sheet_names:

        print(f"✓ {feuille}")

    donnees = {}

    for feuille_attendue in FEUILLES_ATTENDUES:

        feuille_reelle = trouver_feuille(
            fichier.sheet_names,
            feuille_attendue
        )

        if feuille_reelle is None:

            raise ValueError(
                f"Feuille introuvable : "
                f"{feuille_attendue}"
            )

        df = pd.read_excel(
            EXCEL_PATH,
            sheet_name=feuille_reelle
        )

        df = normaliser_colonnes(
            df
        )

        donnees[
            feuille_attendue
        ] = df

    return donnees


# ============================================================
# NETTOYAGE DES DONNÉES
# ============================================================

def nettoyer_dataframe(df):
    """
    Remplace les NaN par None et supprime
    les espaces inutiles dans les chaînes.
    """

    df = df.where(
        pd.notna(df),
        None
    )

    for colonne in df.columns:

        df[colonne] = df[colonne].apply(
            lambda valeur:
            valeur.strip()
            if isinstance(valeur, str)
            else valeur
        )

    return df


# ============================================================
# AFFICHER LA STRUCTURE DU FICHIER
# ============================================================

def verifier_colonnes(donnees):

    print("\n========================================")
    print("     STRUCTURE DU FICHIER EXCEL")
    print("========================================")

    for nom_feuille, df in donnees.items():

        print("\n" + "=" * 60)
        print(f"FEUILLE : {nom_feuille}")
        print("=" * 60)

        print(
            f"\nNombre de lignes    : {len(df)}"
        )

        print(
            f"Nombre de colonnes  : {len(df.columns)}"
        )

        print("\nColonnes normalisées :")

        for numero, colonne in enumerate(
            df.columns,
            start=1
        ):

            print(
                f"{numero}. {colonne}"
            )

        print("\nAperçu des données :")

        if df.empty:

            print(
                "⚠️ Feuille vide."
            )

        else:

            print(
                df.head(5).to_string(
                    index=False
                )
            )


# ============================================================
# IMPORTATION DES NOEUDS
# ============================================================

def importer_noeuds(df, connection):

    if df.empty:
        return 0

    df = nettoyer_dataframe(df)

    colonnes = [
        "node_id",
        "nom",
        "type",
        "latitude",
        "longitude"
    ]

    for colonne in colonnes:

        if colonne not in df.columns:

            raise ValueError(
                f"NOEUDS : colonne "
                f"'{colonne}' absente."
            )

    requete = text("""
        INSERT INTO noeuds (
            node_id,
            nom,
            type,
            latitude,
            longitude
        )
        VALUES (
            :node_id,
            :nom,
            :type,
            :latitude,
            :longitude
        )
    """)

    compteur = 0

    for _, ligne in df.iterrows():

        connection.execute(
            requete,
            {
                "node_id": ligne["node_id"],
                "nom": ligne["nom"],
                "type": ligne["type"],
                "latitude": ligne["latitude"],
                "longitude": ligne["longitude"]
            }
        )

        compteur += 1

    return compteur


# ============================================================
# IMPORTATION DES CONDUITES
# ============================================================

def importer_conduites(df, connection):

    if df.empty:
        return 0

    df = nettoyer_dataframe(df)

    colonnes = [
        "pipe_id",
        "nom",
        "noeud_depart",
        "noeud_arrivee",
        "diametre_mm",
        "materiau",
        "statut"
    ]

    for colonne in colonnes:

        if colonne not in df.columns:

            raise ValueError(
                f"CONDUITES : colonne "
                f"'{colonne}' absente."
            )

    requete = text("""
        INSERT INTO conduites (
            pipe_id,
            nom,
            noeud_depart,
            noeud_arrivee,
            diametre_mm,
            materiau,
            statut
        )
        VALUES (
            :pipe_id,
            :nom,
            :noeud_depart,
            :noeud_arrivee,
            :diametre_mm,
            :materiau,
            :statut
        )
    """)

    compteur = 0

    for _, ligne in df.iterrows():

        connection.execute(
            requete,
            {
                "pipe_id": ligne["pipe_id"],
                "nom": ligne["nom"],
                "noeud_depart": ligne["noeud_depart"],
                "noeud_arrivee": ligne["noeud_arrivee"],
                "diametre_mm": ligne["diametre_mm"],
                "materiau": ligne["materiau"],
                "statut": ligne["statut"]
            }
        )

        compteur += 1

    return compteur


# ============================================================
# IMPORTATION DES POINTS DES CONDUITES
# ============================================================

def importer_points_conduites(df, connection):

    if df.empty:
        return 0

    df = nettoyer_dataframe(df)

    colonnes = [
        "pipe_id",
        "ordre",
        "latitude",
        "longitude"
    ]

    for colonne in colonnes:

        if colonne not in df.columns:

            raise ValueError(
                f"POINTS_CONDUITES : "
                f"colonne '{colonne}' absente."
            )

    requete = text("""
        INSERT INTO points_conduites (
            pipe_id,
            ordre,
            latitude,
            longitude
        )
        VALUES (
            :pipe_id,
            :ordre,
            :latitude,
            :longitude
        )
    """)

    compteur = 0

    for _, ligne in df.iterrows():

        connection.execute(
            requete,
            {
                "pipe_id": ligne["pipe_id"],
                "ordre": ligne["ordre"],
                "latitude": ligne["latitude"],
                "longitude": ligne["longitude"]
            }
        )

        compteur += 1

    return compteur


# ============================================================
# IMPORTATION DES RESERVOIRS
# ============================================================

def importer_reservoirs(df, connection):

    if df.empty:
        return 0

    df = nettoyer_dataframe(df)

    colonnes = [
        "reservoir_id",
        "nom",
        "node_id",
        "latitude",
        "longitude",
        "altitude_m",
        "capacite_m3",
        "statut",
        "description"
    ]

    for colonne in colonnes:

        if colonne not in df.columns:

            raise ValueError(
                f"RÉSERVOIRS : colonne "
                f"'{colonne}' absente."
            )

    requete = text("""
        INSERT INTO reservoirs (
            reservoir_id,
            nom,
            node_id,
            latitude,
            longitude,
            altitude_m,
            capacite_m3,
            statut,
            description
        )
        VALUES (
            :reservoir_id,
            :nom,
            :node_id,
            :latitude,
            :longitude,
            :altitude_m,
            :capacite_m3,
            :statut,
            :description
        )
    """)

    compteur = 0

    for _, ligne in df.iterrows():

        connection.execute(
            requete,
            {
                "reservoir_id": ligne["reservoir_id"],
                "nom": ligne["nom"],
                "node_id": ligne["node_id"],
                "latitude": ligne["latitude"],
                "longitude": ligne["longitude"],
                "altitude_m": ligne["altitude_m"],
                "capacite_m3": ligne["capacite_m3"],
                "statut": ligne["statut"],
                "description": ligne["description"]
            }
        )

        compteur += 1

    return compteur


# ============================================================
# IMPORTATION DES VANNES
# ============================================================

def importer_vannes(df, connection):

    if df.empty:
        return 0

    df = nettoyer_dataframe(df)

    colonnes = [
        "vanne_id",
        "nom",
        "node_id",
        "latitude",
        "longitude",
        "type_vanne",
        "statut",
        "description"
    ]

    for colonne in colonnes:

        if colonne not in df.columns:

            raise ValueError(
                f"VANNES : colonne "
                f"'{colonne}' absente."
            )

    requete = text("""
        INSERT INTO vannes (
            vanne_id,
            nom,
            node_id,
            latitude,
            longitude,
            type_vanne,
            statut,
            description
        )
        VALUES (
            :vanne_id,
            :nom,
            :node_id,
            :latitude,
            :longitude,
            :type_vanne,
            :statut,
            :description
        )
    """)

    compteur = 0

    for _, ligne in df.iterrows():

        connection.execute(
            requete,
            {
                "vanne_id": ligne["vanne_id"],
                "nom": ligne["nom"],
                "node_id": ligne["node_id"],
                "latitude": ligne["latitude"],
                "longitude": ligne["longitude"],
                "type_vanne": ligne["type_vanne"],
                "statut": ligne["statut"],
                "description": ligne["description"]
            }
        )

        compteur += 1

    return compteur


# ============================================================
# IMPORTATION DES BORNES-FONTAINES
# ============================================================

def importer_bornes(df, connection):

    if df.empty:
        return 0

    df = nettoyer_dataframe(df)

    colonnes = [
        "borne_id",
        "nom",
        "node_id",
        "latitude",
        "longitude",
        "quartier",
        "statut",
        "description"
    ]

    for colonne in colonnes:

        if colonne not in df.columns:

            raise ValueError(
                f"BORNES_FONTAINES : "
                f"colonne '{colonne}' absente."
            )

    requete = text("""
        INSERT INTO bornes_fontaines (
            borne_id,
            nom,
            node_id,
            latitude,
            longitude,
            quartier,
            statut,
            description
        )
        VALUES (
            :borne_id,
            :nom,
            :node_id,
            :latitude,
            :longitude,
            :quartier,
            :statut,
            :description
        )
    """)

    compteur = 0

    for _, ligne in df.iterrows():

        connection.execute(
            requete,
            {
                "borne_id": ligne["borne_id"],
                "nom": ligne["nom"],
                "node_id": ligne["node_id"],
                "latitude": ligne["latitude"],
                "longitude": ligne["longitude"],
                "quartier": ligne["quartier"],
                "statut": ligne["statut"],
                "description": ligne["description"]
            }
        )

        compteur += 1

    return compteur


# ============================================================
# IMPORTATION COMPLÈTE DANS SQLITE
# ============================================================

def importer_dans_sqlite(donnees):

    print("\n========================================")
    print("     IMPORTATION VERS SQLITE")
    print("========================================")

    with engine.begin() as connection:

        # ----------------------------------------------------
        # Nettoyage des anciennes données
        # ----------------------------------------------------

        print(
            "\n🧹 Nettoyage des anciennes données..."
        )

        connection.execute(
            text("DELETE FROM points_conduites")
        )

        connection.execute(
            text("DELETE FROM conduites")
        )

        connection.execute(
            text("DELETE FROM reservoirs")
        )

        connection.execute(
            text("DELETE FROM vannes")
        )

        connection.execute(
            text("DELETE FROM bornes_fontaines")
        )

        connection.execute(
            text("DELETE FROM noeuds")
        )

        # ----------------------------------------------------
        # Importation
        # ----------------------------------------------------

        n_noeuds = importer_noeuds(
            donnees["NOEUDS"],
            connection
        )

        print(
            f"✓ NOEUDS : {n_noeuds}"
        )

        n_conduites = importer_conduites(
            donnees["CONDUITES"],
            connection
        )

        print(
            f"✓ CONDUITES : {n_conduites}"
        )

        n_points = importer_points_conduites(
            donnees["POINTS_CONDUITES"],
            connection
        )

        print(
            f"✓ POINTS_CONDUITES : {n_points}"
        )

        n_reservoirs = importer_reservoirs(
            donnees["RÉSERVOIRS"],
            connection
        )

        print(
            f"✓ RÉSERVOIRS : {n_reservoirs}"
        )

        n_vannes = importer_vannes(
            donnees["VANNES"],
            connection
        )

        print(
            f"✓ VANNES : {n_vannes}"
        )

        n_bornes = importer_bornes(
            donnees["BORNES_FONTAINES"],
            connection
        )

        print(
            f"✓ BORNES_FONTAINES : {n_bornes}"
        )

    print(
        "\n✅ Importation terminée."
    )


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    try:

        print(
            "\n========================================"
        )

        print(
            "     SERVICE EXCEL - KADUTU"
        )

        print(
            "========================================"
        )

        # 1. Lecture du fichier Excel
        donnees = lire_excel()

        # 2. Affichage de la structure
        verifier_colonnes(
            donnees
        )

        # 3. Importation SQLite
        importer_dans_sqlite(
            donnees
        )

        print(
            "\n========================================"
        )

        print(
            "🎉 IMPORTATION RÉUSSIE"
        )

        print(
            "========================================"
        )

    except Exception as erreur:

        print(
            "\n========================================"
        )

        print(
            "❌ ERREUR"
        )

        print(
            "========================================"
        )

        print(
            f"{type(erreur).__name__}: {erreur}"
        )