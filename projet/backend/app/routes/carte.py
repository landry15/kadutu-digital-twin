from fastapi import APIRouter, HTTPException

from app.services.geo_service import obtenir_reseau_geojson


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/carte",
    tags=["Carte"]
)


# ============================================================
# RESEAU COMPLET
# ============================================================

@router.get("/reseau")
def obtenir_carte_reseau():

    try:

        reseau = obtenir_reseau_geojson()

        return {
            "success": True,
            "message": "Réseau de Kadutu récupéré avec succès",
            "data": reseau
        }

    except Exception as erreur:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du réseau : {str(erreur)}"
        )