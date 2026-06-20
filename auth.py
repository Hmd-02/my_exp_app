"""
Protection minimale par mot de passe partagé.
Suffisant pour un usage perso : empêche un visiteur random qui tombe sur ton
URL Streamlit Cloud publique d'accéder à tes données financières.
Ce n'est PAS une authentification multi-utilisateurs sécurisée.
"""
import streamlit as st


def check_password() -> bool:
    """Affiche un formulaire de mot de passe. Retourne True si déverrouillé."""

    def password_entered():
        if st.session_state["password"] == st.secrets["app"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Mot de passe", type="password",
        on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Mot de passe incorrect")
    return False
