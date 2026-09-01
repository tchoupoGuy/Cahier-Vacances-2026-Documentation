"""L'agence de voyage — interface Streamlit branchée directement sur src/.

Contrairement au notebook d'origine (qui régénérait un fichier agent.py à
partir du code du notebook), cette version importe directement les modules
de src/ : une seule source de vérité pour la logique de l'agent.

Pour la lancer, depuis la racine du projet :
    streamlit run webapp/app.py
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.booking import book_trip
from src.agent.planner import plan_trip
from src.data.brochures import load_brochures
from src.data.database import connect, query
from src.embeddings.encoder import load_encoder
from src.tools.flights import find_flights
from src.tools.hotels import find_hotels

st.set_page_config(page_title="Agence de voyage", page_icon="🧳", layout="wide")


@st.cache_resource(show_spinner="Chargement de l'encodeur de phrases (une seule fois)...")
def encoder_en_cache():
    return load_encoder()


@st.cache_data(show_spinner="Lecture des brochures d'hôtels...")
def brochures_en_cache():
    return load_brochures()


# La connexion SQLite n'est PAS mise en cache : Streamlit rejoue le script dans un autre
# thread à chaque interaction, et une connexion sqlite3 n'aime pas changer de thread.
conn = connect()
brochures = brochures_en_cache()
encoder = encoder_en_cache()

VILLES = sorted(query(conn, "SELECT DISTINCT destination FROM vols")["destination"])
PREMIER_JOUR, DERNIER_JOUR = dt.date(2026, 7, 1), dt.date(2026, 8, 31)

st.title("🧳 Où partez-vous ?")
st.caption("Un agent qui cherche, compare, arbitre quand le budget ne suit pas, "
           "et vous dit ce qu'il a sacrifié.")

with st.form("recherche"):
    haut_gauche, haut_milieu, haut_droite = st.columns([2, 1, 2])

    with haut_gauche:
        destination = st.selectbox("Destination", VILLES, index=VILLES.index("Madrid") if "Madrid" in VILLES else 0)
    with haut_milieu:
        voyageurs = st.number_input("Voyageurs", min_value=1, max_value=6, value=2, step=1)
    with haut_droite:
        sejour = st.date_input("Dates du séjour",
                                value=(dt.date(2026, 8, 12), dt.date(2026, 8, 16)),
                                min_value=PREMIER_JOUR, max_value=DERNIER_JOUR,
                                format="DD/MM/YYYY",
                                help="Choisissez la date d'aller, puis celle du retour.")

    budget = st.number_input("Budget par personne, tout compris (€)",
                              min_value=150, max_value=5000, value=750, step=50)

    envie = st.text_area("Ce que vous recherchez",
                          value="un hôtel pour la famille avec une piscine, "
                                "et des visites dans la ville", height=110,
                          help="Écrivez librement : un modèle d'embeddings compare votre "
                               "phrase aux brochures des hôtels, ce n'est pas une recherche "
                               "par mots-clés.")

    _, milieu, _ = st.columns([2, 1, 2])
    with milieu:
        valider = st.form_submit_button("Valider", type="primary", width="stretch")

if len(sejour) != 2:
    st.info("Choisissez aussi une date de retour dans le calendrier.")
    st.stop()

depart, retour = sejour
nuits = (retour - depart).days

if nuits < 1:
    st.warning("Le retour doit tomber au moins un jour après le départ.")
    st.stop()

if valider:
    st.session_state.derniere_recherche = dict(
        destination=destination, depart=depart, retour=retour,
        nuits=nuits, voyageurs=voyageurs, budget=budget, envie=envie)
    st.session_state.confirmation = False

if "derniere_recherche" not in st.session_state:
    st.info("Remplissez le formulaire ci-dessus, puis cliquez sur **Valider**.")
    st.stop()

recherche = st.session_state.derniere_recherche
destination, depart, retour = recherche["destination"], recherche["depart"], recherche["retour"]
nuits, voyageurs = recherche["nuits"], recherche["voyageurs"]
budget, envie = recherche["budget"], recherche["envie"]

# --------------------------------------------------------------------------------------
# Le branchement de l'agent (l'Étape 6 du notebook, ici déjà câblé sur src/).
# --------------------------------------------------------------------------------------
date_texte = depart.strftime("%Y-%m-%d")
demande = {
    "destination": destination, "date_depart": date_texte, "nuits": nuits,
    "voyageurs": voyageurs, "budget_max": budget, "envie": envie,
}
voyage, journal = plan_trip(demande, conn, brochures, encoder)

st.divider()

if voyage is None:
    st.error(f"**Aucun voyage possible à {destination} avec {budget} € par personne.**")
    if journal:
        st.write("Voici tout ce que l'agent a essayé avant d'abandonner :")
        for ligne in journal:
            st.write(f"- {ligne}")
    st.info("Remontez le budget, réduisez le nombre de nuits, ou partez un autre jour : "
            "les vols du week-end sont nettement plus chers.")
    st.stop()

vol, hotel = voyage["vol"], voyage["hotel"]

st.subheader(f"{destination}, du {depart.strftime('%d/%m')} au {retour.strftime('%d/%m/%Y')} "
             f"({nuits} nuits, {voyageurs} voyageur(s))")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Vol", f"{vol['prix_eur']:.0f} €", delta=f"{vol['origine']} · {vol['heure_depart']}",
          delta_color="off")
c2.metric("Hôtel", f"{hotel['prix_nuit'] * nuits:.0f} €",
          delta=f"{hotel['prix_nuit']:.0f} €/nuit", delta_color="off")
c3.metric("Activités", f"{sum(a['prix_eur'] for a in voyage['activites']):.0f} €",
          delta=f"{len(voyage['activites'])} sortie(s)", delta_color="off")
c4.metric("Total par personne", f"{voyage['prix_total']:.0f} €",
          delta=f"{voyage['prix_total'] - budget:.0f} € vs budget", delta_color="inverse")

st.caption(f"Soit **{voyage['prix_total'] * voyageurs:.0f} €** pour {voyageurs} voyageur(s).")

if journal:
    st.warning("**Ce que j'ai fait, et ce que j'ai remarqué :**\n\n"
               + "\n".join(f"- {ligne}" for ligne in journal))
else:
    st.success("Tout rentrait dans le budget, je n'ai rien eu à sacrifier.")

gauche, droite = st.columns(2)

with gauche:
    st.subheader(f"🏨 {hotel['hotel']}")
    st.write("⭐" * int(hotel["etoiles"]) + f"  ·  **{hotel['note']:.1f}/10** "
             f"({int(hotel['avis'])} avis)  ·  pertinence {hotel['score']:.2f}")
    st.write(hotel["texte"])

with droite:
    st.subheader("🎫 Votre programme")
    if voyage["activites"]:
        for a in voyage["activites"]:
            st.write(f"**{a['nom']}** ({a['categorie']}) : {a['duree_h']:.0f} h, {a['prix_eur']:.0f} €")
    else:
        st.write("_Aucune activité : le budget ne le permettait pas._")

    st.subheader("✈️ Le vol retenu")
    st.write(f"**{vol['numero']}** · {vol['origine']} → {destination} · "
             f"{depart.strftime('%d/%m/%Y')} à {vol['heure_depart']} · {vol['duree_h']:.0f} h de vol")

with st.expander("Voir ce que l'agent a consulté avant de décider"):
    g, d = st.columns(2)
    with g:
        st.write("**Les vols disponibles ce jour-là**")
        st.dataframe(find_flights(conn, destination, demande["date_depart"], voyageurs).head(15),
                     hide_index=True, width="stretch")
    with d:
        st.write("**Les hôtels les plus proches de votre demande**")
        st.dataframe(find_hotels(brochures, encoder, destination, demande["envie"])
                     [["hotel", "etoiles", "note", "prix_nuit", "score"]],
                     hide_index=True, width="stretch")

st.divider()
st.subheader("Réserver")

nom_gauche, bouton_droite = st.columns([3, 1])
with nom_gauche:
    client = st.text_input("À quel nom ?", value="", placeholder="Votre nom")
with bouton_droite:
    st.write("")
    st.write("")
    if st.button("Réserver ce voyage", width="stretch"):
        st.session_state.confirmation = True

if st.session_state.get("confirmation"):
    if not client.strip():
        st.warning("Indiquez d'abord un nom.")
    else:
        st.info(book_trip(conn, voyage, client.strip()))
        _, centre, _ = st.columns([2, 1, 2])
        with centre:
            if st.button("Oui, je confirme", type="primary", width="stretch"):
                st.success(book_trip(conn, voyage, client.strip(), confirme=True))
                st.session_state.confirmation = False
                st.balloons()

st.caption("Vols, hôtels et activités sont des données fabriquées pour le cahier de vacances. "
           "Ne préparez pas de vraies vacances avec.")
