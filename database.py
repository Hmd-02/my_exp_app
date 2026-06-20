"""
Centralise tous les accès à la base de données Supabase.
Garder toute la logique "données" ici évite de mélanger SQL et affichage
dans le reste de l'app — si demain tu changes de base, tu ne modifies que ce fichier.
"""
import streamlit as st
from st_supabase_connection import SupabaseConnection, execute_query
from datetime import date


def get_connection():
    """Retourne la connexion Supabase, mise en cache par Streamlit."""
    return st.connection(
        name="supabase",
        type=SupabaseConnection,
    )


# ---------- CATEGORIES ----------

def get_categories(conn, type_filtre: str | None = None):
    """
    Récupère les catégories. type_filtre = 'depense', 'revenu', ou None pour toutes.
    ttl court : les catégories changent rarement, on peut cacher plus longtemps.
    """
    query = conn.table("categorie").select("*")
    if type_filtre:
        query = query.eq("type", type_filtre)
    result = execute_query(query.order("nom"), ttl="5m")
    return result.data


def create_default_categories(conn):
    """Insère les catégories par défaut si la table est vide (premier lancement)."""
    existing = execute_query(conn.table("categorie").select("id"), ttl=0)
    if existing.data:
        return  # déjà initialisé

    defaults = [
        {"nom": "Alimentation", "type": "depense", "icone": "🍽️"},
        {"nom": "Transport", "type": "depense", "icone": "🚗"},
        {"nom": "Logement", "type": "depense", "icone": "🏠"},
        {"nom": "Loisirs", "type": "depense", "icone": "🎮"},
        {"nom": "Santé", "type": "depense", "icone": "💊"},
        {"nom": "Abonnements", "type": "depense", "icone": "📱"},
        {"nom": "Autres dépenses", "type": "depense", "icone": "📦"},
        {"nom": "Salaire", "type": "revenu", "icone": "💼"},
        {"nom": "Freelance", "type": "revenu", "icone": "💻"},
        {"nom": "Autres revenus", "type": "revenu", "icone": "✨"},
    ]
    conn.table("categorie").insert(defaults).execute()


# ---------- TRANSACTIONS ----------

def add_transaction(conn, montant: float, type_t: str, categorie_id: str,
                     date_t: date, note: str = ""):
    """Insère une nouvelle transaction."""
    conn.table("transaction").insert({
        "montant": montant,
        "type": type_t,
        "categorie_id": categorie_id,
        "date": date_t.isoformat(),
        "note": note,
    }).execute()
    st.cache_data.clear()  # force le rechargement des données affichées


def get_transactions(conn, date_debut: date | None = None, date_fin: date | None = None):
    """Récupère les transactions, avec le nom de catégorie joint, triées par date desc."""
    query = conn.table("transaction").select("*, categorie(nom, icone, type)")
    if date_debut:
        query = query.gte("date", date_debut.isoformat())
    if date_fin:
        query = query.lte("date", date_fin.isoformat())
    result = execute_query(query.order("date", desc=True), ttl=0)
    return result.data


def delete_transaction(conn, transaction_id: str):
    conn.table("transaction").delete().eq("id", transaction_id).execute()
    st.cache_data.clear()
