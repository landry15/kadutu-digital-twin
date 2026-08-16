from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import carte


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Kadutu Digital Twin API",
    description=(
        "API du jumeau numérique du réseau "
        "de fourniture d'eau de Kadutu"
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(
    carte.router
)


# ============================================================
# ROUTE PRINCIPALE
# ============================================================

@app.get("/")
def accueil():

    return {
        "message": "Kadutu Digital Twin API",
        "status": "online"
    }


# ============================================================
# TEST
# ============================================================

@app.get("/api/health")
def health_check():

    return {
        "status": "ok",
        "message": "API fonctionnelle"
    }