# src/escala_vovo/config/auth.py
"""Sistema de autenticação de administrador"""

from passlib.hash import bcrypt
import streamlit as st


ADMIN_PASSWORD_HASH = "$2b$12$oLZHqXuWe1YopeJMQAk77.bxwIL1ySQvHb8g9j2AJ5gsaalSTbUKW"


def verificar_senha_admin(senha: str) -> bool:
    if not senha:
        return False
    try:
        return bcrypt.verify(senha, ADMIN_PASSWORD_HASH)
    except Exception:
        return False


def is_admin_autenticado() -> bool:
    return st.session_state.get("is_admin", False)


def fazer_login_admin():
    st.session_state["is_admin"] = True


def fazer_logout_admin():
    st.session_state["is_admin"] = False
