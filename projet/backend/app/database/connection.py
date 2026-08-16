from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# CONFIGURATION DE LA BASE DE DONNÉES
# ============================================================

DATABASE_URL = "sqlite:///./tutore.db"


# ============================================================
# CRÉATION DU MOTEUR SQLITE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# ============================================================
# SESSION DE BASE DE DONNÉES
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# BASE DES MODÈLES SQLALCHEMY
# ============================================================

Base = declarative_base()


# ============================================================
# DÉPENDANCE FASTAPI
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()