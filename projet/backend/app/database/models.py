from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship

from .connection import Base


# ============================================================
# TABLE : NOEUDS
# ============================================================

class Noeud(Base):
    __tablename__ = "noeuds"

    id = Column(Integer, primary_key=True, index=True)

    node_id = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(150), nullable=False)
    type = Column(String(100), nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    altitude_m = Column(Float, nullable=True)

    statut = Column(String(50), default="Actif")
    description = Column(Text, nullable=True)

    # Relations avec les conduites
    conduites_depart = relationship(
        "Conduite",
        foreign_keys="Conduite.noeud_depart",
        back_populates="depart"
    )

    conduites_arrivee = relationship(
        "Conduite",
        foreign_keys="Conduite.noeud_arrivee",
        back_populates="arrivee"
    )


# ============================================================
# TABLE : CONDUITES
# ============================================================

class Conduite(Base):
    __tablename__ = "conduites"

    id = Column(Integer, primary_key=True, index=True)

    pipe_id = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(150), nullable=False)

    noeud_depart = Column(
        String(50),
        ForeignKey("noeuds.node_id"),
        nullable=False
    )

    noeud_arrivee = Column(
        String(50),
        ForeignKey("noeuds.node_id"),
        nullable=False
    )

    diametre_mm = Column(Float, nullable=True)
    materiau = Column(String(100), nullable=True)
    type_conduite = Column(String(100), nullable=True)

    statut = Column(String(50), default="Active")

    longueur_m = Column(Float, nullable=True)

    description = Column(Text, nullable=True)

    # Relations avec les nœuds
    depart = relationship(
        "Noeud",
        foreign_keys=[noeud_depart],
        back_populates="conduites_depart"
    )

    arrivee = relationship(
        "Noeud",
        foreign_keys=[noeud_arrivee],
        back_populates="conduites_arrivee"
    )

    # Points géographiques de la conduite
    points = relationship(
        "PointConduite",
        back_populates="conduite",
        cascade="all, delete-orphan",
        order_by="PointConduite.ordre"
    )


# ============================================================
# TABLE : POINTS_CONDUITES
# ============================================================

class PointConduite(Base):
    __tablename__ = "points_conduites"

    id = Column(Integer, primary_key=True, index=True)

    pipe_id = Column(
        String(50),
        ForeignKey("conduites.pipe_id"),
        nullable=False,
        index=True
    )

    ordre = Column(Integer, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    altitude_m = Column(Float, nullable=True)

    conduite = relationship(
        "Conduite",
        back_populates="points"
    )


# ============================================================
# TABLE : RESERVOIRS
# ============================================================

class Reservoir(Base):
    __tablename__ = "reservoirs"

    id = Column(Integer, primary_key=True, index=True)

    reservoir_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    nom = Column(String(150), nullable=False)

    node_id = Column(
        String(50),
        ForeignKey("noeuds.node_id"),
        nullable=False
    )

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    altitude_m = Column(Float, nullable=True)

    capacite_m3 = Column(Float, nullable=True)

    statut = Column(String(50), default="Actif")

    description = Column(Text, nullable=True)


# ============================================================
# TABLE : VANNES
# ============================================================

class Vanne(Base):
    __tablename__ = "vannes"

    id = Column(Integer, primary_key=True, index=True)

    vanne_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    nom = Column(String(150), nullable=False)

    node_id = Column(
        String(50),
        ForeignKey("noeuds.node_id"),
        nullable=False
    )

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    type_vanne = Column(String(100), nullable=True)

    statut = Column(String(50), default="Active")

    description = Column(Text, nullable=True)


# ============================================================
# TABLE : BORNES FONTAINES
# ============================================================

class BorneFontaine(Base):
    __tablename__ = "bornes_fontaines"

    id = Column(Integer, primary_key=True, index=True)

    borne_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    nom = Column(String(150), nullable=False)

    node_id = Column(
        String(50),
        ForeignKey("noeuds.node_id"),
        nullable=False
    )

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    quartier = Column(String(150), nullable=True)

    statut = Column(String(50), default="Active")

    description = Column(Text, nullable=True)