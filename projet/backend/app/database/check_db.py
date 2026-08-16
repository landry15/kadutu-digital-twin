from sqlalchemy import inspect
from .connection import engine


def check_database():
    print("\n========================================")
    print("     VÉRIFICATION DE LA BASE TUTORE")
    print("========================================\n")

    inspector = inspect(engine)

    # Récupération des tables
    tables = inspector.get_table_names()

    if not tables:
        print("❌ Aucune table trouvée.")
        return

    print(f"✅ {len(tables)} table(s) trouvée(s) :\n")

    for table in tables:
        print(f"📋 Table : {table}")

        columns = inspector.get_columns(table)

        for column in columns:
            name = column["name"]
            column_type = column["type"]
            nullable = column["nullable"]

            print(
                f"   ├── {name} "
                f"({column_type}) "
                f"{'NULL' if nullable else 'NOT NULL'}"
            )

        print()

    print("========================================")
    print("✅ Vérification terminée")
    print("========================================")


if __name__ == "__main__":
    check_database()