from sqlalchemy import text

from app.database.connection import engine


# ============================================================
# CONFIGURATION
# ============================================================

TABLES = [
    "noeuds",
    "conduites",
    "points_conduites",
    "reservoirs",
    "vannes",
    "bornes_fontaines"
]


# ============================================================
# COMPTER LES ENREGISTREMENTS
# ============================================================

def compter_enregistrements(connection, table):

    resultat = connection.execute(
        text(
            f"SELECT COUNT(*) FROM {table}"
        )
    )

    return resultat.scalar()


# ============================================================
# AFFICHER LES DONNÉES
# ============================================================

def afficher_donnees(connection, table):

    resultat = connection.execute(
        text(
            f"SELECT * FROM {table}"
        )
    )

    lignes = resultat.fetchall()

    if not lignes:

        print(
            "   ⚠️ Aucune donnée."
        )

        return

    for ligne in lignes:

        print(
            f"   {dict(ligne._mapping)}"
        )


# ============================================================
# VÉRIFICATION
# ============================================================

def verifier_base():

    print("\n========================================")
    print("     VÉRIFICATION DE TUTORE.DB")
    print("========================================")

    with engine.connect() as connection:

        total_general = 0

        for table in TABLES:

            print(
                f"\n📋 Table : {table}"
            )

            try:

                nombre = compter_enregistrements(
                    connection,
                    table
                )

                print(
                    f"   Nombre d'enregistrements : "
                    f"{nombre}"
                )

                total_general += nombre

                afficher_donnees(
                    connection,
                    table
                )

            except Exception as erreur:

                print(
                    f"   ❌ Erreur : {erreur}"
                )

        print("\n========================================")
        print(
            f"TOTAL DES ENREGISTREMENTS : "
            f"{total_general}"
        )
        print("========================================")


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    try:

        verifier_base()

        print(
            "\n✅ Vérification terminée."
        )

    except Exception as erreur:

        print(
            "\n❌ ERREUR"
        )

        print(
            f"{type(erreur).__name__}: {erreur}"
        )