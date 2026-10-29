# src/escala_vovo/config/auth.py
"""Sistema de autenticação de administrador"""

from passlib.hash import bcrypt
import streamlit as st


# COLE AQUI o hash que você gerou no passo 2
ADMIN_PASSWORD_HASH = "$2b$12$oLZHqXuWe1YopeJMQAk77.bxwIL1ySQvHb8g9j2AJ5gsaalSTbUKW"


def verificar_senha_admin(senha: str) -> bool:
    """Verifica se a senha de administrador está correta"""
    if not senha:
        return False
    try:
        return bcrypt.verify(senha, ADMIN_PASSWORD_HASH)
    except Exception:
        return False


def is_admin_autenticado() -> bool:
    """Verifica se o usuário atual está autenticado como admin"""
    return st.session_state.get("is_admin", False)


def fazer_login_admin():
    """Marca a sessão como administrador"""
    st.session_state["is_admin"] = True


def fazer_logout_admin():
    """Remove privilégios de administrador"""
    st.session_state["is_admin"] = False