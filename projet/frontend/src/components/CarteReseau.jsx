import {
    MapContainer,
    TileLayer,
    GeoJSON,
    LayersControl,
    useMap
} from "react-leaflet";

import {
    useEffect,
    useMemo,
    useRef,
    useState
} from "react";

import axios from "axios";

import L from "leaflet";

import "./CarteReseau.css";


const API_URL = "http://127.0.0.1:8000";


const CENTRE_KADUTU = [
    -2.5000,
    28.8600
];


/* ============================================================
   AJUSTER AUTOMATIQUEMENT LA VUE
============================================================ */

function AjusterVue({ reseau }) {

    const map = useMap();

    useEffect(() => {

        if (!reseau) {
            return;
        }

        const bounds = L.latLngBounds([]);


        const ajouterCoordonnees = (geojson) => {

            if (!geojson?.features) {
                return;
            }


            geojson.features.forEach(
                (feature) => {

                    const geometry =
                        feature.geometry;


                    if (!geometry) {
                        return;
                    }


                    if (
                        geometry.type === "Point"
                    ) {

                        const [
                            longitude,
                            latitude
                        ] = geometry.coordinates;


                        if (
                            Number.isFinite(latitude) &&
                            Number.isFinite(longitude)
                        ) {

                            bounds.extend([
                                latitude,
                                longitude
                            ]);

                        }

                    }


                    if (
                        geometry.type === "LineString"
                    ) {

                        geometry.coordinates.forEach(
                            ([longitude, latitude]) => {

                                if (
                                    Number.isFinite(latitude) &&
                                    Number.isFinite(longitude)
                                ) {

                                    bounds.extend([
                                        latitude,
                                        longitude
                                    ]);

                                }

                            }
                        );

                    }

                }
            );

        };


        Object.values(reseau).forEach(
            ajouterCoordonnees
        );


        if (bounds.isValid()) {

            map.fitBounds(
                bounds,
                {
                    padding: [40, 40],
                    maxZoom: 17
                }
            );

        }

    }, [reseau, map]);


    return null;
}


/* ============================================================
   COULEUR DES CONDUITES
============================================================ */

/* ============================================================
   STYLE DYNAMIQUE DES CONDUITES
============================================================ */

function styleConduite(feature) {

    const etat =
        determinerEtatConduite(
            feature
        );


    switch (etat) {

        case "Fuite suspectée":

            return {
                color: "#dc2626",
                weight: 7,
                opacity: 1,
                dashArray: "10, 8"
            };


        case "Faible pression":

            return {
                color: "#f97316",
                weight: 6,
                opacity: 0.95
            };


        case "Maintenance":

            return {
                color: "#eab308",
                weight: 6,
                opacity: 0.95,
                dashArray: "8, 6"
            };


        case "Hors service":

            return {
                color: "#4b5563",
                weight: 5,
                opacity: 0.8,
                dashArray: "5, 8"
            };


        case "Active":

        default:

            return {
                color: "#16a34a",
                weight: 5,
                opacity: 0.9
            };

    }
}


/* ============================================================
   ICÔNES
============================================================ */

function creerIcone(
    emoji,
    classe
) {

    return L.divIcon({

        className:
            `icone-reseau ${classe}`,

        html: `
            <div class="icone-reseau-contenu">
                ${emoji}
            </div>
        `,

        iconSize: [36, 36],

        iconAnchor: [18, 18],

        popupAnchor: [0, -18]

    });

}

/* ============================================================
   DETERMINER L'ETAT DYNAMIQUE D'UNE CONDUITE
============================================================ */

function determinerEtatConduite(feature) {

    const p = feature.properties || {};

    const statut = String(
        p.statut || ""
    ).toLowerCase();


    /*
     * Les états suivants seront plus tard
     * calculés avec les données des capteurs
     * et du modèle IA.
     */

    if (
        statut.includes("hors") ||
        statut.includes("inactive")
    ) {
        return "Hors service";
    }


    if (
        statut.includes("maintenance") ||
        statut.includes("entretien")
    ) {
        return "Maintenance";
    }


    /*
     * Pour le moment :
     * une conduite active est considérée
     * comme fonctionnant normalement.
     */

    return "Active";
}

const iconeReservoir =
    creerIcone(
        "🏗️",
        "icone-reservoir"
    );


const iconeVanne =
    creerIcone(
        "🔧",
        "icone-vanne"
    );


const iconeBorne =
    creerIcone(
        "🚰",
        "icone-borne"
    );


/* ============================================================
   POPUP CONDUITE
============================================================ */

function onEachConduite(
    feature,
    layer
) {

    const p =
        feature.properties || {};
    const etat = 
        determinerEtatConduite(
        feature
    );

    layer.bindPopup(`
        <div class="popup-reseau">

            <h3>
                🚰 ${p.nom || "Conduite"}
            </h3>

            <div>
                <strong>ID :</strong>
                ${p.pipe_id || "-"}
            </div>

            <div>
                <strong>Départ :</strong>
                ${p.noeud_depart || "-"}
            </div>

            <div>
                <strong>Arrivée :</strong>
                ${p.noeud_arrivee || "-"}
            </div>

            <div>
                <strong>Diamètre :</strong>
                ${p.diametre_mm || "-"} mm
            </div>

            <div>
                <strong>Matériau :</strong>
                ${p.materiau || "-"}
            </div>

            <div>
                <strong>Statut :</strong>
                ${p.statut || "-"}
            </div>

            <div class="etat-conduite">
                <strong>État du réseau :</strong>

                <span class="badge-etat">
                    ${etat}
                </span>
            </div>

            <hr>

            <div>
                <strong>Pression :</strong>
                <span class="future-value">
                    --
                </span>
            </div>

            <div>
                <strong>Débit :</strong>
                <span class="future-value">
                    --
                </span>
            </div>

            <div>
                <strong>Anomalie IA :</strong>
                <span class="future-value">
                    Aucune donnée
                </span>
            </div>

        </div>
    `);

}


/* ============================================================
   POPUP NOEUD
============================================================ */

function onEachNoeud(
    feature,
    layer
) {

    const p =
        feature.properties || {};


    layer.bindPopup(`
        <div class="popup-reseau">

            <h3>
                📍 ${p.nom || "Nœud"}
            </h3>

            <div>
                <strong>ID :</strong>
                ${p.node_id || "-"}
            </div>

            <div>
                <strong>Type :</strong>
                ${p.type || "-"}
            </div>

        </div>
    `);

}


/* ============================================================
   POPUP RESERVOIR
============================================================ */

function onEachReservoir(
    feature,
    layer
) {

    const p =
        feature.properties || {};


    layer.bindPopup(`
        <div class="popup-reseau">

            <h3>
                🏗️ ${p.nom || "Réservoir"}
            </h3>

            <div>
                <strong>ID :</strong>
                ${p.reservoir_id || "-"}
            </div>

            <div>
                <strong>Nœud :</strong>
                ${p.node_id || "-"}
            </div>

            <div>
                <strong>Capacité :</strong>
                ${p.capacite_m3 ?? "-"} m³
            </div>

            <div>
                <strong>Altitude :</strong>
                ${p.altitude_m ?? "-"} m
            </div>

            <div>
                <strong>Statut :</strong>
                ${p.statut || "-"}
            </div>

        </div>
    `);

}


/* ============================================================
   POPUP VANNE
============================================================ */

function onEachVanne(
    feature,
    layer
) {

    const p =
        feature.properties || {};


    layer.bindPopup(`
        <div class="popup-reseau">

            <h3>
                🔧 ${p.nom || "Vanne"}
            </h3>

            <div>
                <strong>ID :</strong>
                ${p.vanne_id || "-"}
            </div>

            <div>
                <strong>Nœud :</strong>
                ${p.node_id || "-"}
            </div>

            <div>
                <strong>Type :</strong>
                ${p.type_vanne || "-"}
            </div>

            <div>
                <strong>Statut :</strong>
                ${p.statut || "-"}
            </div>

        </div>
    `);

}


/* ============================================================
   POPUP BORNE
============================================================ */

function onEachBorne(
    feature,
    layer
) {

    const p =
        feature.properties || {};


    layer.bindPopup(`
        <div class="popup-reseau">

            <h3>
                🚰 ${p.nom || "Borne-fontaine"}
            </h3>

            <div>
                <strong>ID :</strong>
                ${p.borne_id || "-"}
            </div>

            <div>
                <strong>Nœud :</strong>
                ${p.node_id || "-"}
            </div>

            <div>
                <strong>Quartier :</strong>
                ${p.quartier || "-"}
            </div>

            <div>
                <strong>Statut :</strong>
                ${p.statut || "-"}
            </div>

        </div>
    `);

}


/* ============================================================
   COMPOSANT PRINCIPAL
============================================================ */

function CarteReseau() {

    const [reseau, setReseau] =
        useState(null);

    const [chargement, setChargement] =
        useState(true);

    const [erreur, setErreur] =
        useState(null);

    const [recherche, setRecherche] =
        useState("");


    /*
     * Référence vers les couches Leaflet.
     */
    const layersRef =
        useRef({});


    /* ========================================================
       CHARGEMENT DU RESEAU
    ======================================================== */

    useEffect(() => {

        async function chargerReseau() {

            try {

                setChargement(true);


                const response =
                    await axios.get(
                        `${API_URL}/api/carte/reseau`
                    );


                if (
                    !response.data?.data
                ) {

                    throw new Error(
                        "Réponse API invalide."
                    );

                }


                setReseau(
                    response.data.data
                );

                setErreur(null);

            } catch (error) {

                console.error(
                    error
                );

                setErreur(
                    "Impossible de charger le réseau."
                );

            } finally {

                setChargement(false);

            }

        }


        chargerReseau();

    }, []);


    /* ========================================================
       RECHERCHE
    ======================================================== */

    const resultatsRecherche =
        useMemo(() => {

            if (
                !reseau ||
                !recherche.trim()
            ) {

                return [];

            }


            const terme =
                recherche
                    .toLowerCase()
                    .trim();


            const couches = [
                "conduites",
                "reservoirs",
                "vannes",
                "bornes_fontaines",
                "noeuds"
            ];


            const resultats = [];


            couches.forEach(
                (nomCouche) => {

                    const couche =
                        reseau[nomCouche];


                    if (
                        !couche?.features
                    ) {

                        return;

                    }


                    couche.features.forEach(
                        (feature) => {

                            const proprietes =
                                feature.properties || {};


                            const texte =
                                Object.values(
                                    proprietes
                                )
                                .filter(
                                    (valeur) =>
                                        valeur !== null &&
                                        valeur !== undefined
                                )
                                .join(" ")
                                .toLowerCase();


                            if (
                                texte.includes(
                                    terme
                                )
                            ) {

                                resultats.push({
                                    couche:
                                        nomCouche,
                                    feature
                                });

                            }

                        }
                    );

                }
            );


            return resultats.slice(
                0,
                10
            );

        }, [
            recherche,
            reseau
        ]);


    /* ========================================================
       FONCTION DE RECHERCHE
    ======================================================== */

    const obtenirIdentifiant =
        (feature, couche) => {

            const p =
                feature.properties || {};


            switch (couche) {

                case "conduites":
                    return p.pipe_id;

                case "reservoirs":
                    return p.reservoir_id;

                case "vannes":
                    return p.vanne_id;

                case "bornes_fontaines":
                    return p.borne_id;

                case "noeuds":
                    return p.node_id;

                default:
                    return null;

            }

        };


    /* ========================================================
       SELECTION D'UN RESULTAT
    ======================================================== */

    const selectionnerElement = (
        resultat
    ) => {

        const {
            couche,
            feature
        } = resultat;


        const identifiant =
            obtenirIdentifiant(
                feature,
                couche
            );


        if (!identifiant) {
            return;
        }


        const layer =
            layersRef.current[
                `${couche}:${identifiant}`
            ];


        if (!layer) {

            console.warn(
                "Couche non trouvée :",
                couche,
                identifiant
            );

            return;

        }


        /*
         * Pour une conduite :
         * calculer les limites de toute la ligne.
         */

        if (
            typeof layer.getBounds ===
            "function"
        ) {

            const bounds =
                layer.getBounds();


            if (bounds.isValid()) {

                window.dispatchEvent(
                    new CustomEvent(
                        "centrer-reseau",
                        {
                            detail: {
                                bounds
                            }
                        }
                    )
                );

            }

        }


        /*
         * Pour les éléments ponctuels.
         */

        else if (
            typeof layer.getLatLng ===
            "function"
        ) {

            const latlng =
                layer.getLatLng();


            window.dispatchEvent(
                new CustomEvent(
                    "centrer-point",
                    {
                        detail: {
                            latlng
                        }
                    }
                )
            );

        }


        /*
         * Ouvrir le popup.
         */

        if (
            typeof layer.openPopup ===
            "function"
        ) {

            layer.openPopup();

        }


        /*
         * Fermer les résultats.
         */

        setRecherche("");

    };


    /* ========================================================
       ETATS
    ======================================================== */

    if (chargement) {

        return (
            <div className="carte-message">
                Chargement du réseau de Kadutu...
            </div>
        );

    }


    if (erreur) {

        return (
            <div className="carte-message erreur">
                {erreur}
            </div>
        );

    }


    if (!reseau) {

        return (
            <div className="carte-message">
                Aucun réseau disponible.
            </div>
        );

    }


    return (

        <div className="carte-wrapper">


            {/* =================================================
                RECHERCHE
            ================================================= */}

            <div className="carte-recherche">

                <div className="recherche-titre">
                    🗺️ Réseau d'eau de Kadutu
                </div>


                <input
                    type="search"
                    value={recherche}
                    onChange={(e) =>
                        setRecherche(
                            e.target.value
                        )
                    }
                    placeholder={
                        "P001, R001, V001, BF001..."
                    }
                />


                {recherche &&
                    resultatsRecherche.length === 0 && (

                    <div className="aucun-resultat">
                        Aucun élément trouvé.
                    </div>

                )}


                {resultatsRecherche.length > 0 && (

                    <div className="resultats-recherche">

                        {resultatsRecherche.map(
                            (
                                resultat,
                                index
                            ) => {

                                const p =
                                    resultat
                                        .feature
                                        .properties || {};


                                const nom =
                                    p.nom ||
                                    p.pipe_id ||
                                    p.reservoir_id ||
                                    p.vanne_id ||
                                    p.borne_id ||
                                    p.node_id ||
                                    "Élément";


                                return (

                                    <button
                                        key={index}
                                        type="button"
                                        onClick={() =>
                                            selectionnerElement(
                                                resultat
                                            )
                                        }
                                    >

                                        <strong>
                                            {nom}
                                        </strong>

                                        <span>
                                            {resultat.couche}
                                        </span>

                                    </button>

                                );

                            }
                        )}

                    </div>

                )}

            </div>


            {/* =================================================
                CARTE
            ================================================= */}

            <MapContainer

                center={
                    CENTRE_KADUTU
                }

                zoom={14}

                scrollWheelZoom={true}

                className="carte"

            >

                <TileLayer

                    attribution={
                        '&copy; OpenStreetMap contributors'
                    }

                    url={
                        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    }

                />


                <AjusterVue
                    reseau={reseau}
                />


                <GestionRecherche />


                <LayersControl
                    position="topright"
                >


                    {/* =========================================
                        CONDUITES
                    ========================================= */}

                    <LayersControl.Overlay
                        checked
                        name="🚰 Conduites"
                    >

                        <GeoJSON

                            data={
                                reseau.conduites
                            }

                            style={
                                styleConduite
                            }

                            onEachFeature={(
                                feature,
                                layer
                            ) => {

                                onEachConduite(
                                    feature,
                                    layer
                                );


                                const id =
                                    feature
                                        .properties
                                        ?.pipe_id;


                                if (id) {

                                    layersRef.current[
                                        `conduites:${id}`
                                    ] = layer;

                                }

                            }}

                        />

                    </LayersControl.Overlay>


                    {/* =========================================
                        NOEUDS
                    ========================================= */}

                    <LayersControl.Overlay
                        checked
                        name="📍 Nœuds"
                    >

                        <GeoJSON

                            data={
                                reseau.noeuds
                            }

                            pointToLayer={(
                                feature,
                                latlng
                            ) => {

                                return L.circleMarker(
                                    latlng,
                                    {
                                        radius: 6,
                                        color: "#1f2937",
                                        weight: 2,
                                        fillColor: "#ffffff",
                                        fillOpacity: 1
                                    }
                                );

                            }}

                            onEachFeature={(
                                feature,
                                layer
                            ) => {

                                onEachNoeud(
                                    feature,
                                    layer
                                );


                                const id =
                                    feature
                                        .properties
                                        ?.node_id;


                                if (id) {

                                    layersRef.current[
                                        `noeuds:${id}`
                                    ] = layer;

                                }

                            }}

                        />

                    </LayersControl.Overlay>


                    {/* =========================================
                        RESERVOIRS
                    ========================================= */}

                    <LayersControl.Overlay
                        checked
                        name="🏗️ Réservoirs"
                    >

                        <GeoJSON

                            data={
                                reseau.reservoirs
                            }

                            pointToLayer={(
                                feature,
                                latlng
                            ) => {

                                return L.marker(
                                    latlng,
                                    {
                                        icon:
                                            iconeReservoir
                                    }
                                );

                            }}

                            onEachFeature={(
                                feature,
                                layer
                            ) => {

                                onEachReservoir(
                                    feature,
                                    layer
                                );


                                const id =
                                    feature
                                        .properties
                                        ?.reservoir_id;


                                if (id) {

                                    layersRef.current[
                                        `reservoirs:${id}`
                                    ] = layer;

                                }

                            }}

                        />

                    </LayersControl.Overlay>


                    {/* =========================================
                        VANNES
                    ========================================= */}

                    <LayersControl.Overlay
                        checked
                        name="🔧 Vannes"
                    >

                        <GeoJSON

                            data={
                                reseau.vannes
                            }

                            pointToLayer={(
                                feature,
                                latlng
                            ) => {

                                return L.marker(
                                    latlng,
                                    {
                                        icon:
                                            iconeVanne
                                    }
                                );

                            }}

                            onEachFeature={(
                                feature,
                                layer
                            ) => {

                                onEachVanne(
                                    feature,
                                    layer
                                );


                                const id =
                                    feature
                                        .properties
                                        ?.vanne_id;


                                if (id) {

                                    layersRef.current[
                                        `vannes:${id}`
                                    ] = layer;

                                }

                            }}

                        />

                    </LayersControl.Overlay>


                    {/* =========================================
                        BORNES
                    ========================================= */}

                    <LayersControl.Overlay
                        checked
                        name="🚰 Bornes-fontaines"
                    >

                        <GeoJSON

                            data={
                                reseau.bornes_fontaines
                            }

                            pointToLayer={(
                                feature,
                                latlng
                            ) => {

                                return L.marker(
                                    latlng,
                                    {
                                        icon:
                                            iconeBorne
                                    }
                                );

                            }}

                            onEachFeature={(
                                feature,
                                layer
                            ) => {

                                onEachBorne(
                                    feature,
                                    layer
                                );


                                const id =
                                    feature
                                        .properties
                                        ?.borne_id;


                                if (id) {

                                    layersRef.current[
                                        `bornes_fontaines:${id}`
                                    ] = layer;

                                }

                            }}

                        />

                    </LayersControl.Overlay>


                </LayersControl>


            </MapContainer>


            {/* =================================================
                LEGENDE
            ================================================= */}

            <div className="legende-carte">

                <div className="legende-titre">
                    Légende
                </div>


                <div className="legende-item">

                    <span
                        className="ligne active"
                    />

                    Conduite active

                </div>


                <div className="legende-item">

                    <span
                        className="ligne maintenance"
                    />

                    Maintenance

                </div>


                <div className="legende-item">

                    <span
                        className="ligne inactive"
                    />

                    Hors service

                </div>


                <div className="legende-item">
                    🏗️ Réservoir
                </div>


                <div className="legende-item">
                    🔧 Vanne
                </div>


                <div className="legende-item">
                    🚰 Borne-fontaine
                </div>


                <div className="legende-item">
                    📍 Nœud
                </div>

            </div>


            {/* =================================================
                INDICATEURS
            ================================================= */}

            <div className="indicateurs-futurs">

                <div>
                    <span>
                        Pression
                    </span>

                    <strong>
                        -- bar
                    </strong>
                </div>


                <div>
                    <span>
                        Débit
                    </span>

                    <strong>
                        -- m³/h
                    </strong>
                </div>


                <div>
                    <span>
                        Anomalies IA
                    </span>

                    <strong>
                        --
                    </strong>
                </div>

            </div>

        </div>

    );

}


/* ============================================================
   CONTROLE DE LA CARTE
============================================================ */

function GestionRecherche() {

    const map = useMap();


    useEffect(() => {

        const centrerReseau = (
            event
        ) => {

            const bounds =
                event.detail?.bounds;


            if (
                bounds &&
                bounds.isValid()
            ) {

                map.fitBounds(
                    bounds,
                    {
                        padding: [80, 80],
                        maxZoom: 18
                    }
                );

            }

        };


        const centrerPoint = (
            event
        ) => {

            const latlng =
                event.detail?.latlng;


            if (!latlng) {
                return;
            }


            map.flyTo(
                latlng,
                18,
                {
                    duration: 1
                }
            );

        };


        window.addEventListener(
            "centrer-reseau",
            centrerReseau
        );


        window.addEventListener(
            "centrer-point",
            centrerPoint
        );


        return () => {

            window.removeEventListener(
                "centrer-reseau",
                centrerReseau
            );


            window.removeEventListener(
                "centrer-point",
                centrerPoint
            );

        };

    }, [map]);


    return null;
}


export default CarteReseau;