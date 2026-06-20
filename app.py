import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.express as px



from auth import check_password
from database import (
    get_connection, get_categories, create_default_categories,
    add_transaction, get_transactions, delete_transaction,
)

st.set_page_config(page_title="Mes finances", page_icon="💰", layout="centered")

# --- Protection par mot de passe ---
if not check_password():
    st.stop()

# --- Connexion + initialisation ---
conn = get_connection()
create_default_categories(conn)

st.title("💰 Mes finances")

onglet_saisie, onglet_historique, onglet_stats = st.tabs(
    ["➕ Ajouter", "📋 Historique", "📊 Statistiques"]
)

# =====================================================
# ONGLET 1 : SAISIE
# =====================================================
with onglet_saisie:
    type_transaction = st.radio(
        "Type", ["Dépense", "Revenu"], horizontal=True
    )
    type_code = "depense" if type_transaction == "Dépense" else "revenu"

    categories = get_categories(conn, type_filtre=type_code)
    options_categories = {f"{c['icone']} {c['nom']}": c["id"] for c in categories}

    with st.form("form_ajout", clear_on_submit=True):
        montant = st.number_input("Montant (€)", min_value=0.0, step=1.0, format="%.2f")
        categorie_label = st.selectbox("Catégorie", options_categories.keys())
        date_transaction = st.date_input("Date", value=date.today())
        note = st.text_input("Note (optionnel)")

        submit = st.form_submit_button("Enregistrer", use_container_width=True)
        if submit:
            if montant <= 0:
                st.error("Le montant doit être supérieur à 0.")
            else:
                add_transaction(
                    conn, montant, type_code,
                    options_categories[categorie_label],
                    date_transaction, note,
                )
                st.success("Transaction enregistrée !")
                st.rerun()

# =====================================================
# ONGLET 2 : HISTORIQUE
# =====================================================
with onglet_historique:
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Du", value=date.today().replace(day=1), key="hist_debut")
    with col2:
        date_fin = st.date_input("Au", value=date.today(), key="hist_fin")

    transactions = get_transactions(conn, date_debut, date_fin)

    if not transactions:
        st.info("Aucune transaction sur cette période.")
    else:
        solde_periode = sum(
            t["montant"] if t["type"] == "revenu" else -t["montant"]
            for t in transactions
        )
        st.metric("Solde sur la période", f"{solde_periode:,.2f} €")

        for t in transactions:
            cat = t.get("categorie") or {}
            signe = "+" if t["type"] == "revenu" else "-"
            couleur = "green" if t["type"] == "revenu" else "red"
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(
                    f"{cat.get('icone', '')} **{cat.get('nom', 'Sans catégorie')}** "
                    f"— {t['date']}  \n"
                    f":{couleur}[{signe}{t['montant']:.2f} €] "
                    f"{('· ' + t['note']) if t.get('note') else ''}"
                )
            with col_b:
                if st.button("🗑️", key=f"del_{t['id']}"):
                    delete_transaction(conn, t["id"])
                    st.rerun()
            st.divider()

# =====================================================
# ONGLET 3 : STATISTIQUES
# =====================================================
with onglet_stats:
    periode = st.selectbox(
        "Période", ["Ce mois-ci", "30 derniers jours", "Cette année", "Tout"]
    )

    today = date.today()
    if periode == "Ce mois-ci":
        date_debut_stats = today.replace(day=1)
    elif periode == "30 derniers jours":
        date_debut_stats = today - timedelta(days=30)
    elif periode == "Cette année":
        date_debut_stats = today.replace(month=1, day=1)
    else:
        date_debut_stats = None

    transactions_stats = get_transactions(conn, date_debut_stats, today)

    if not transactions_stats:
        st.info("Pas encore de données pour cette période.")
    else:
        df = pd.DataFrame(transactions_stats)
        df["categorie_nom"] = df["categorie"].apply(
            lambda c: c.get("nom", "Sans catégorie") if c else "Sans catégorie"
        )

        total_depenses = df.loc[df["type"] == "depense", "montant"].sum()
        total_revenus = df.loc[df["type"] == "revenu", "montant"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Revenus", f"{total_revenus:,.2f} €")
        col2.metric("Dépenses", f"{total_depenses:,.2f} €")
        col3.metric("Solde", f"{total_revenus - total_depenses:,.2f} €")

        st.subheader("Répartition des dépenses par catégorie")
        df_depenses = df[df["type"] == "depense"]
        if not df_depenses.empty:
            par_categorie = df_depenses.groupby("categorie_nom")["montant"].sum().reset_index()
            fig_pie = px.pie(
                par_categorie, names="categorie_nom", values="montant", hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.caption("Aucune dépense sur cette période.")

        st.subheader("Évolution dans le temps")
        df["date"] = pd.to_datetime(df["date"])
        evolution = df.groupby([df["date"].dt.to_period("D").astype(str), "type"])["montant"] \
            .sum().reset_index()
        fig_line = px.bar(
            evolution, x="date", y="montant", color="type", barmode="group"
        )
        st.plotly_chart(fig_line, use_container_width=True)




