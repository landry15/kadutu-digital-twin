import json

from sqlalchemy import text

from app.database.connection import engine


# ============================================================
# OUTILS GEOJSON
# ============================================================

def creer_point(latitude, longitude, proprietes=None):
    """
    Crée une Feature GeoJSON de type Point.
    """

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                float(longitude),
                float(latitude)
            ]
        },
        "properties": proprietes or {}
    }


def creer_ligne(points, proprietes=None):
    """
    Crée une Feature GeoJSON de type LineString.

    points doit contenir :
        [(latitude, longitude), ...]
    """

    return {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [
                    float(longitude),
                    float(latitude)
                ]
                for latitude, longitude in points
            ]
        },
        "properties": proprietes or {}
    }


def creer_feature_collection(features):
    """
    Crée une FeatureCollection GeoJSON.
    """

    return {
        "type": "FeatureCollection",
        "features": features
    }


# ============================================================
# NOEUDS
# ============================================================

def obtenir_noeuds(connection):

    resultat = connection.execute(
        text("""
            SELECT
                node_id,
                nom,
                type,
                latitude,
                longitude
            FROM noeuds
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
            ORDER BY node_id
        """)
    )

    features = []

    for ligne in resultat:

        proprietes = {
            "node_id": ligne.node_id,
            "nom": ligne.nom,
            "type": ligne.type
        }

        features.append(
            creer_point(
                ligne.latitude,
                ligne.longitude,
                proprietes
            )
        )

    return creer_feature_collection(
        features
    )


# ============================================================
# CONDUITES
# ============================================================

def obtenir_conduites(connection):

    resultat = connection.execute(
        text("""
            SELECT
                pipe_id,
                nom,
                noeud_depart,
                noeud_arrivee,
                diametre_mm,
                materiau,
                statut
            FROM conduites
            ORDER BY pipe_id
        """)
    )

    features = []

    for conduite in resultat:

        points_resultat = connection.execute(
            text("""
                SELECT
                    ordre,
                    latitude,
                    longitude
                FROM points_conduites
                WHERE pipe_id = :pipe_id
                  AND latitude IS NOT NULL
                  AND longitude IS NOT NULL
                ORDER BY ordre
            """),
            {
                "pipe_id": conduite.pipe_id
            }
        )

        points = [
            (
                point.latitude,
                point.longitude
            )
            for point in points_resultat
        ]

        # Une ligne nécessite au minimum
        # deux coordonnées.
        if len(points) < 2:
            continue

        proprietes = {
            "pipe_id": conduite.pipe_id,
            "nom": conduite.nom,
            "noeud_depart": conduite.noeud_depart,
            "noeud_arrivee": conduite.noeud_arrivee,
            "diametre_mm": conduite.diametre_mm,
            "materiau": conduite.materiau,
            "statut": conduite.statut
        }

        features.append(
            creer_ligne(
                points,
                proprietes
            )
        )

    return creer_feature_collection(
        features
    )


# ============================================================
# RESERVOIRS
# ============================================================

def obtenir_reservoirs(connection):

    resultat = connection.execute(
        text("""
            SELECT
                reservoir_id,
                nom,
                node_id,
                latitude,
                longitude,
                altitude_m,
                capacite_m3,
                statut,
                description
            FROM reservoirs
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
            ORDER BY reservoir_id
        """)
    )

    features = []

    for ligne in resultat:

        proprietes = {
            "reservoir_id": ligne.reservoir_id,
            "nom": ligne.nom,
            "node_id": ligne.node_id,
            "altitude_m": ligne.altitude_m,
            "capacite_m3": ligne.capacite_m3,
            "statut": ligne.statut,
            "description": ligne.description
        }

        features.append(
            creer_point(
                ligne.latitude,
                ligne.longitude,
                proprietes
            )
        )

    return creer_feature_collection(
        features
    )


# ============================================================
# VANNES
# ============================================================

def obtenir_vannes(connection):

    resultat = connection.execute(
        text("""
            SELECT
                vanne_id,
                nom,
                node_id,
                latitude,
                longitude,
                type_vanne,
                statut,
                description
            FROM vannes
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
            ORDER BY vanne_id
        """)
    )

    features = []

    for ligne in resultat:

        proprietes = {
            "vanne_id": ligne.vanne_id,
            "nom": ligne.nom,
            "node_id": ligne.node_id,
            "type_vanne": ligne.type_vanne,
            "statut": ligne.statut,
            "description": ligne.description
        }

        features.append(
            creer_point(
                ligne.latitude,
                ligne.longitude,
                proprietes
            )
        )

    return creer_feature_collection(
        features
    )


# ============================================================
# BORNES-FONTAINES
# ============================================================

def obtenir_bornes(connection):

    resultat = connection.execute(
        text("""
            SELECT
                borne_id,
                nom,
                node_id,
                latitude,
                longitude,
                quartier,
                statut,
                description
            FROM bornes_fontaines
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
            ORDER BY borne_id
        """)
    )

    features = []

    for ligne in resultat:

        proprietes = {
            "borne_id": ligne.borne_id,
            "nom": ligne.nom,
            "node_id": ligne.node_id,
            "quartier": ligne.quartier,
            "statut": ligne.statut,
            "description": ligne.description
        }

        features.append(
            creer_point(
                ligne.latitude,
                ligne.longitude,
                proprietes
            )
        )

    return creer_feature_collection(
        features
    )


# ============================================================
# RESEAU COMPLET
# ============================================================

def obtenir_reseau_geojson():

    with engine.connect() as connection:

        reseau = {

            "noeuds": obtenir_noeuds(
                connection
            ),

            "conduites": obtenir_conduites(
                connection
            ),

            "reservoirs": obtenir_reservoirs(
                connection
            ),

            "vannes": obtenir_vannes(
                connection
            ),

            "bornes_fontaines": obtenir_bornes(
                connection
            )
        }

    return reseau


# ============================================================
# SAUVEGARDE GEOJSON
# ============================================================

def sauvegarder_geojson(
    chemin="data/reseau_kadutu.geojson"
):

    reseau = obtenir_reseau_geojson()

    # On regroupe toutes les features
    features = []

    for couche in reseau.values():

        features.extend(
            couche["features"]
        )

    geojson = creer_feature_collection(
        features
    )

    with open(
        chemin,
        "w",
        encoding="utf-8"
    ) as fichier:

        json.dump(
            geojson,
            fichier,
            ensure_ascii=False,
            indent=4
        )

    return geojson


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    try:

        print("\n========================================")
        print("     SERVICE CARTOGRAPHIQUE")
        print("        KADUTU DIGITAL TWIN")
        print("========================================")

        reseau = obtenir_reseau_geojson()

        print("\n📍 NOEUDS")

        print(
            f"   {len(reseau['noeuds']['features'])} "
            f"élément(s)"
        )

        print("\n🚰 CONDUITES")

        print(
            f"   {len(reseau['conduites']['features'])} "
            f"élément(s)"
        )

        print("\n🏗️ RESERVOIRS")

        print(
            f"   {len(reseau['reservoirs']['features'])} "
            f"élément(s)"
        )

        print("\n🔧 VANNES")

        print(
            f"   {len(reseau['vannes']['features'])} "
            f"élément(s)"
        )

        print("\n🚰 BORNES-FONTAINES")

        print(
            f"   {len(reseau['bornes_fontaines']['features'])} "
            f"élément(s)"
        )

        # ----------------------------------------------------
        # Sauvegarde
        # ----------------------------------------------------

        chemin = "data/reseau_kadutu.geojson"

        sauvegarder_geojson(
            chemin
        )

        print(
            "\n========================================"
        )

        print(
            "✅ GEOJSON CRÉÉ AVEC SUCCÈS"
        )

        print(
            f"📁 Fichier : {chemin}"
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