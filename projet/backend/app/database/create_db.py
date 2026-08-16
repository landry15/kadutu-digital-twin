from .connection import engine, Base
from . import models


def create_database():
    print("Création de la base de données...")

    Base.metadata.create_all(bind=engine)

    print("Base de données créée avec succès.")


if __name__ == "__main__":
    create_database()