# src/escala_vovo/app.py
"""Aplicação principal - Escala da Vovó"""

import streamlit as st
from datetime import date, time
import uuid

# Imports do projeto
from escala_vovo.core.models import Cuidador, Turno
from escala_vovo.core.rules import RegrasEscala
from escala_vovo.services.calendar_service import CalendarService
from escala_vovo.infrastructure.repository import Repository
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
    return Repository("data/escala.json")


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

    # Monta HTML do calendário
    html = '<div class="calendario-grid">'

    # Cabeçalhos
    for dia_semana in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]:
        html += f'<div class="calendario-header">{dia_semana}</div>'

    # Células vazias antes do primeiro dia
    for _ in range(offset):
        html += '<div class="calendario-dia vazio"></div>'

    # Dias do mês
    for dia_info in estrutura:
        tipo = "weekend" if dia_info['is_fim_semana'] else "weekday"

        html += f'<div class="calendario-dia {tipo}">'
        html += f'<div class="calendario-numero">{dia_info["dia"]}</div>'
        html += f'<div class="calendario-semana">{dia_info["dia_semana_curto"]}</div>'

        turnos_dia = repo.listar_turnos_por_data(dia_info['data'])
        for t in turnos_dia:
            cuidador = repo.buscar_cuidador(t['cuidador_id'])
            if cuidador:
                html += (
                    f'<div class="calendario-turno" '
                    f'style="background:{cuidador["cor"]};">'
                    f'{cuidador["nome"]}</div>'
                )

        html += '</div>'

    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)

    # ============================================
    # ÁREA DE ADMINISTRAÇÃO (fora do grid)
    # ============================================
    if is_admin:
        st.markdown("---")
        st.markdown("### ➕ Adicionar Turno")

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            dias_opcoes = {d['data_formatada']: d['data'] for d in estrutura}
            dia_escolhido_str = st.selectbox("Dia", list(dias_opcoes.keys()))
            dia_escolhido = dias_opcoes[dia_escolhido_str]

        with col2:
            cuidadores = repo.listar_cuidadores_ativos()
            if cuidadores:
                nomes = [c['nome'] for c in cuidadores]
                cuidador_nome = st.selectbox("Cuidador", nomes)
                cuidador_id = [c['id'] for c in cuidadores if c['nome'] == cuidador_nome][0]
            else:
                st.warning("Cadastre cuidadores primeiro!")
                cuidador_id = None

        with col3:
            st.markdown("<div style='padding-top: 28px;'>", unsafe_allow_html=True)
            if st.button("Adicionar", type="primary"):
                if cuidador_id:
                    turnos_model = repo.to_turnos_model()
                    cuidador_dict = repo.buscar_cuidador(cuidador_id)

                    pode, motivo = RegrasEscala.pode_alocar(
                        cuidador_id, dia_escolhido,
                        turnos_model, cuidador_dict
                    )

                    if pode:
                        turno = Turno(
                            id=str(uuid.uuid4())[:8],
                            data=dia_escolhido,
                            cuidador_id=cuidador_id,
                        )
                        repo.adicionar_turno(turno)
                        st.success("✅ Adicionado!")
                        st.rerun()
                    else:
                        st.error(f"❌ {motivo}")
            st.markdown("</div>", unsafe_allow_html=True)

        # ============================================
        # REMOVER TURNOS
        # ============================================
        st.markdown("---")
        st.markdown("### 🗑️ Remover Turno")

        turnos_mes = [
            t for t in repo.listar_turnos()
            if t['data'].startswith(f"{ano}-{mes:02d}")
        ]

        if turnos_mes:
            for t in turnos_mes:
                cuidador = repo.buscar_cuidador(t['cuidador_id'])
                if cuidador:
                    data_fmt = date.fromisoformat(t['data']).strftime('%d/%m/%Y')
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.write(f"**{data_fmt}** — {cuidador['nome']}")
                    with col_b:
                        if st.button("🗑️", key=f"del_turno_{t['id']}"):
                            repo.remover_turno(t['id'])
                            st.rerun()
        else:
            st.info("Nenhum turno cadastrado neste mês.")

# ============================================
# TAB 2: CUIDADORES (apenas admin)
# ============================================
if tab2 is not None:
    with tab2:
        st.markdown("### 👥 Gerenciar Cuidadores")

        cuidadores = repo.listar_cuidadores()

        if cuidadores:
            for c in cuidadores:
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(
                        f'<div class="cuidador-card" style="border-left-color:{c["cor"]};">'
                        f'<b>{c["nome"]}</b>'
                        + (f' • 📞 {c["telefone"]}' if c.get('telefone') else '')
                        + '</div>',
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(f"**Ativo:** {'✅' if c['ativo'] else '❌'}")

                with col3:
                    if st.button("🗑️", key=f"del_{c['id']}"):
                        repo.remover_cuidador(c['id'])
                        st.rerun()
        else:
            st.info("Nenhum cuidador cadastrado.")

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