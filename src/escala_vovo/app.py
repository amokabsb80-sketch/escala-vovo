# src/escala_vovo/app.py
"""Aplicação principal - Escala da Vovó"""

import streamlit as st
from datetime import date, time
import uuid

# Imports do projeto
from escala_vovo.core.models import Cuidador, Turno
from escala_vovo.core.rules import RegrasEscala
from escala_vovo.services.calendar_service import CalendarService
from escala_vovo.infrastructure.supabase_repository import SupabaseRepository
from escala_vovo.config.auth import (
    verificar_senha_admin, is_admin_autenticado,
    fazer_login_admin, fazer_logout_admin
)

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Escala da Vovó",
    page_icon="👵",
    layout="wide",
)


# ============================================
# INICIALIZAÇÃO
# ============================================
@st.cache_resource
def get_repository():
    return SupabaseRepository()


repo = get_repository()

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa, #e4e8eb);
    }

    .header-title {
        text-align: center;
        color: #2c3e50;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0;
    }

    .header-subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.2em;
        margin-top: 0;
    }

    .cuidador-card {
        background: white;
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 5px solid;
    }

    /* ============================================
       CALENDÁRIO - CSS GRID (ALINHAMENTO PERFEITO)
       ============================================ */
    .calendario-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 6px;
        width: 100%;
    }

    .calendario-header {
        text-align: center;
        font-weight: bold;
        color: #2c3e50;
        padding: 8px 0;
        background: #ecf0f1;
        border-radius: 6px;
        font-size: 0.9em;
    }

    .calendario-dia {
        min-height: 110px;
        border-radius: 8px;
        padding: 6px;
        box-sizing: border-box;
        font-size: 0.85em;
        position: relative;
    }

    .calendario-dia.weekday {
        background: #f8fbff;
        border-left: 4px solid #3498db;
    }

    .calendario-dia.weekend {
        background: #fff5f5;
        border-left: 4px solid #e74c3c;
    }

    .calendario-dia.vazio {
        background: transparent;
        border: none;
    }

    .calendario-numero {
        font-weight: bold;
        font-size: 1.1em;
        color: #2c3e50;
    }

    .calendario-semana {
        color: #7f8c8d;
        font-size: 0.75em;
        margin-bottom: 4px;
    }

    .calendario-turno {
        color: white;
        border-radius: 4px;
        padding: 2px 5px;
        margin: 2px 0;
        font-size: 0.75em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CABEÇALHO
# ============================================
st.markdown('<h1 class="header-title">👵 Escala da Vovó</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Gerenciamento de cuidadores</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================
# SIDEBAR - CONTROLE DE ACESSO
# ============================================
with st.sidebar:
    st.markdown("## 🔐 Acesso")

    if is_admin_autenticado():
        is_admin = True
        st.success("🔓 Modo Administrador")

        if st.button("🚪 Sair do modo admin"):
            fazer_logout_admin()
            st.rerun()
    else:
        is_admin = False

        with st.expander("🔒 Entrar como administrador"):
            with st.form("form_admin_login"):
                senha = st.text_input(
                    "Senha de administrador",
                    type="password",
                    placeholder="Digite a senha..."
                )
                entrar = st.form_submit_button("Entrar")

                if entrar:
                    if verificar_senha_admin(senha):
                        fazer_login_admin()
                        st.success("✅ Bem-vindo, administrador!")
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta")

    st.markdown("---")

    st.markdown("## 📅 Filtro")
    anos = CalendarService.get_anos_disponiveis()
    ano = st.selectbox("Ano", anos, index=0)

    meses = CalendarService.get_meses(ano)
    nomes_meses = [m[1] for m in meses]
    mes_nome = st.selectbox("Mês", nomes_meses)
    mes = [m[0] for m in meses if m[1] == mes_nome][0]

    st.markdown("---")

    st.markdown("## 📊 Estatísticas")
    stats = repo.estatisticas()
    st.metric("Cuidadores", stats["total_cuidadores"])
    st.metric("Turnos", stats["total_turnos"])

# ============================================
# TABS PRINCIPAIS
# ============================================
if is_admin:
    tab1, tab2, tab3 = st.tabs(["📅 Calendário", "👥 Cuidadores", "⚙️ Configurações"])
else:
    tab1, = st.tabs(["📅 Calendário"])
    tab2 = tab3 = None

# ============================================
# TAB 1: CALENDÁRIO
# ============================================
with tab1:
    st.markdown(f"### 📅 {mes_nome} de {ano}")

    estrutura = CalendarService.get_estrutura_mes(ano, mes)

    primeiro_dia = estrutura[0]['data']
    offset = primeiro_dia.weekday()

    # Cabeçalho
    dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    header_cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        with header_cols[i]:
            st.markdown(
                f"<div style='text-align:center; font-weight:bold; "
                f"background:#ecf0f1; padding:8px; border-radius:6px; "
                f"color:#2c3e50;'>{dia}</div>",
                unsafe_allow_html=True
            )

    # Monta grid
    todas_celulas = [None] * offset + estrutura
    while len(todas_celulas) % 7 != 0:
        todas_celulas.append(None)

    semanas = [todas_celulas[i:i+7] for i in range(0, len(todas_celulas), 7)]

    for semana in semanas:
        cols = st.columns(7)

        for i, dia_info in enumerate(semana):
            with cols[i]:
                if dia_info is None:
                    st.markdown(
                        "<div style='min-height:120px;'></div>",
                        unsafe_allow_html=True
                    )
                    continue

                turnos_dia = repo.listar_turnos_por_data(dia_info['data'])

                bg = "#fff5f5" if dia_info['is_fim_semana'] else "#f8fbff"
                border = "#e74c3c" if dia_info['is_fim_semana'] else "#3498db"

                # Monta HTML SEM indentação (tudo em uma linha por bloco)
                card_html = (
                    f'<div style="background:{bg};border-left:4px solid {border};'
                    f'border-radius:8px;padding:8px;margin:4px 0;min-height:100px;">'
                    f'<div style="font-weight:bold;font-size:1.1em;color:#2c3e50;">'
                    f'{dia_info["dia"]}</div>'
                    f'<div style="color:#7f8c8d;font-size:0.75em;margin-bottom:5px;">'
                    f'{dia_info["dia_semana_curto"]}</div>'
                )

                for t in turnos_dia:
                    cuidador = repo.buscar_cuidador(t['cuidador_id'])
                    if cuidador:
                        card_html += (
                            f'<div style="background:{cuidador["cor"]};color:white;'
                            f'border-radius:5px;padding:3px 6px;margin:2px 0;'
                            f'font-size:0.75em;">{cuidador["nome"]}</div>'
                        )

                card_html += '</div>'
                st.markdown(card_html, unsafe_allow_html=True)

                # Botões (admin)
                if is_admin:
                    col_add, col_rm = st.columns(2)

                    with col_add:
                        with st.popover("➕"):
                            st.markdown(f"**{dia_info['data_formatada']}**")
                            cuidadores = repo.listar_cuidadores_ativos()
                            if cuidadores:
                                nomes = [c['nome'] for c in cuidadores]
                                cuidador_nome = st.selectbox(
                                    "Cuidador", nomes,
                                    key=f"add_{dia_info['data']}"
                                )
                                cuidador_id = [
                                    c['id'] for c in cuidadores
                                    if c['nome'] == cuidador_nome
                                ][0]

                                if st.button("Confirmar",
                                           key=f"btn_{dia_info['data']}"):
                                    turnos_model = repo.to_turnos_model()
                                    cuidador_dict = repo.buscar_cuidador(cuidador_id)
                                    pode, motivo = RegrasEscala.pode_alocar(
                                        cuidador_id, dia_info['data'],
                                        turnos_model, cuidador_dict
                                    )
                                    if pode:
                                        turno = Turno(
                                            id=str(uuid.uuid4())[:8],
                                            data=dia_info['data'],
                                            cuidador_id=cuidador_id,
                                        )
                                        repo.adicionar_turno(turno)
                                        st.success("✅ Adicionado!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {motivo}")
                            else:
                                st.warning("Cadastre cuidadores primeiro!")

                    with col_rm:
                        if turnos_dia:
                            with st.popover("🗑️"):
                                st.markdown(f"**Remover de {dia_info['data_formatada']}**")
                                for t in turnos_dia:
                                    cuidador = repo.buscar_cuidador(t['cuidador_id'])
                                    if cuidador:
                                        if st.button(
                                            f"❌ {cuidador['nome']}",
                                            key=f"rm_{t['id']}"
                                        ):
                                            repo.remover_turno(t['id'])
                                            st.rerun()
# ============================================
# TAB 2: CUIDADORES (apenas admin)
# ============================================
if tab2 is not None:
    with tab2:
        st.markdown("### 👥 Gerenciar Cuidadores")

        # Lista COMPLETA (sem filtro)
        todos_cuidadores = repo.listar_cuidadores()

        if todos_cuidadores:
            # Filtro (em variável separada)
            filtro = st.radio(
                "Mostrar",
                ["Todos", "Ativos", "Inativos"],
                horizontal=True
            )

            if filtro == "Ativos":
                cuidadores_filtrados = [c for c in todos_cuidadores if c['ativo']]
            elif filtro == "Inativos":
                cuidadores_filtrados = [c for c in todos_cuidadores if not c['ativo']]
            else:
                cuidadores_filtrados = todos_cuidadores

            st.markdown("---")

            if not cuidadores_filtrados:
                st.info(f"Nenhum cuidador {filtro.lower()} encontrado.")
            else:
                for c in cuidadores_filtrados:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                    with col1:
                        st.markdown(
                            f'<div class="cuidador-card" style="border-left-color:{c["cor"]};">'
                            f'<b>{c["nome"]}</b>'
                            + (f' • 📞 {c["telefone"]}' if c.get('telefone') else '')
                            + '</div>',
                            unsafe_allow_html=True
                        )

                    with col2:
                        if c['ativo']:
                            st.markdown("**✅ Ativo**")
                        else:
                            st.markdown("**❌ Inativo**")

                    with col3:
                        if c['ativo']:
                            if st.button("Desativar", key=f"toggle_{c['id']}"):
                                repo.atualizar_cuidador(c['id'], ativo=False)
                                st.rerun()
                        else:
                            if st.button("Ativar", key=f"toggle_{c['id']}"):
                                repo.atualizar_cuidador(c['id'], ativo=True)
                                st.rerun()

                    with col4:
                        if st.button("🗑️", key=f"del_{c['id']}"):
                            repo.remover_cuidador(c['id'])
                            st.rerun()
        else:
            st.info("Nenhum cuidador cadastrado ainda.")

        st.markdown("---")
        st.markdown("### ➕ Adicionar Cuidador")

        with st.form("form_cuidador"):
            nome = st.text_input("Nome")
            telefone = st.text_input("Telefone (opcional)")
            cor = st.color_picker("Cor", "#3498db")

            st.markdown("**Disponibilidade:**")
            col_a, col_b = st.columns(2)
            with col_a:
                pode_sabado = st.checkbox("Trabalha aos sábados", value=True)
            with col_b:
                pode_domingo = st.checkbox("Trabalha aos domingos", value=True)

            if st.form_submit_button("Adicionar"):
                if nome:
                    novo = Cuidador(
                        id=str(uuid.uuid4())[:8],
                        nome=nome,
                        telefone=telefone or None,
                        cor=cor,
                        pode_sabado=pode_sabado,
                        pode_domingo=pode_domingo,
                    )
                    repo.adicionar_cuidador(novo)
                    st.success(f"✅ {nome} adicionado!")
                    st.rerun()
                else:
                    st.error("Preencha o nome!")

# ============================================
# TAB 3: CONFIGURAÇÕES (apenas admin)
# ============================================
if tab3 is not None:
    with tab3:
        st.markdown("### ⚙️ Configurações")

        st.markdown("#### Regras atuais")
        st.write(f"- Dias de descanso mínimo: **{RegrasEscala.DIAS_DESCANSO_MINIMO}**")
        st.write(f"- Máximo de turnos por semana: **{RegrasEscala.MAX_TURNOS_POR_SEMANA}**")

        st.markdown("---")
        st.markdown("#### Dados")
        st.write(f"- Cuidadores: {len(repo.listar_cuidadores())}")
        st.write(f"- Turnos: {len(repo.listar_turnos())}")

        st.markdown("---")

        if st.button("🗑️ Limpar TODOS os dados", type="secondary"):
            if st.checkbox("Confirmo que quero apagar tudo"):
                repo.limpar_tudo()
                st.success("Dados apagados!")
                st.rerun()

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#95a5a6; font-size:0.85em;'>"
    "👵 Escala da Vovó • Feito com carinho"
    "</div>",
    unsafe_allow_html=True
)