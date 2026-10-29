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

    .dia-card {
        background: white;
        border-radius: 10px;
        padding: 12px;
        margin: 6px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    .dia-fim-semana {
        background: #fff5f5;
        border-left: 4px solid #e74c3c;
    }

    .dia-semana {
        background: #f8fbff;
        border-left: 4px solid #3498db;
    }

    .dia-numero {
        font-size: 1.3em;
        font-weight: bold;
        color: #2c3e50;
    }

    .dia-nome {
        color: #7f8c8d;
        font-size: 0.9em;
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
# Imports no topo do arquivo (adicione junto aos outros imports)
from escala_vovo.config.auth import (
    verificar_senha_admin, is_admin_autenticado,
    fazer_login_admin, fazer_logout_admin
)

# No sidebar, substitua o bloco:
with st.sidebar:
    st.markdown("## 🔐 Acesso")

    # Verifica se já está logado como admin
    if is_admin_autenticado():
        is_admin = True
        st.success("🔓 Modo Administrador")

        if st.button("🚪 Sair do modo admin"):
            fazer_logout_admin()
            st.rerun()
    else:
        is_admin = False

        # Formulário de senha para admin
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

    # Filtro de ano
    st.markdown("## 📅 Filtro")
    anos = CalendarService.get_anos_disponiveis()
    ano = st.selectbox("Ano", anos, index=0)

    # Filtro de mês
    meses = CalendarService.get_meses(ano)
    nomes_meses = [m[1] for m in meses]
    mes_nome = st.selectbox("Mês", nomes_meses)
    mes = [m[0] for m in meses if m[1] == mes_nome][0]

    st.markdown("---")

    # Estatísticas
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

    # Pega a estrutura do mês
    estrutura = CalendarService.get_estrutura_mes(ano, mes)

    # Mostra em grid (7 colunas = dias da semana)
    cols = st.columns(7)

    # Cabeçalho dos dias da semana
    dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    for i, dia in enumerate(dias_semana):
        with cols[i]:
            st.markdown(f"**{dia}**", help=f"Dia da semana")

    # Primeiro dia do mês: calcula o offset
    primeiro_dia = estrutura[0]['data']
    offset = primeiro_dia.weekday()  # 0=segunda, 6=domingo

    # Preenche com vazios antes do primeiro dia
    col_idx = 0
    for _ in range(offset):
        with cols[col_idx]:
            st.write("")
        col_idx += 1

    # Preenche os dias do mês
    for dia_info in estrutura:
        with cols[col_idx]:
            # Verifica se tem turno neste dia
            turnos_dia = repo.listar_turnos_por_data(dia_info['data'])

            # Estilo baseado no tipo de dia
            bg = "#fff5f5" if dia_info['is_fim_semana'] else "#f8fbff"
            border = "#e74c3c" if dia_info['is_fim_semana'] else "#3498db"

            # Monta conteúdo do card
            conteudo = f"""
            <div style="background:{bg}; border-left:4px solid {border}; 
                        border-radius:8px; padding:8px; margin:4px 0;
                        min-height:100px;">
                <div style="font-weight:bold; font-size:1.1em;">
                    {dia_info['dia']}
                </div>
                <div style="color:#7f8c8d; font-size:0.75em; margin-bottom:5px;">
                    {dia_info['dia_semana_curto']}
                </div>
            """

            # Adiciona turnos
            for t in turnos_dia:
                cuidador = repo.buscar_cuidador(t['cuidador_id'])
                if cuidador:
                    conteudo += f"""
                    <div style="background:{cuidador['cor']}; color:white; 
                                border-radius:5px; padding:3px 6px; 
                                margin:2px 0; font-size:0.75em;">
                        {cuidador['nome']}
                    </div>
                    """

            conteudo += "</div>"

            st.markdown(conteudo, unsafe_allow_html=True)

            # Se admin, permite adicionar turno
            if is_admin:
                with st.popover("➕", help="Adicionar turno"):
                    st.markdown(f"**{dia_info['data_formatada']}**")

                    cuidadores = repo.listar_cuidadores_ativos()
                    if cuidadores:
                        nomes = [c['nome'] for c in cuidadores]
                        cuidador_nome = st.selectbox(
                            "Cuidador", nomes, key=f"add_{dia_info['data']}"
                        )
                        cuidador_id = [
                            c['id'] for c in cuidadores
                            if c['nome'] == cuidador_nome
                        ][0]

                        if st.button("Confirmar", key=f"btn_{dia_info['data']}"):
                            # Verifica regras
                            turnos_model = repo.to_turnos_model()
                            pode, motivo = RegrasEscala.pode_alocar(
                                cuidador_id, dia_info['data'], turnos_model
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

        col_idx += 1
        if col_idx >= 7:
            col_idx = 0

# ============================================
# TAB 2: CUIDADORES (apenas admin)
# ============================================
if tab2 is not None:
    with tab2:
        st.markdown("### 👥 Gerenciar Cuidadores")

        # Lista cuidadores
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

        # Adicionar novo cuidador
        st.markdown("### ➕ Adicionar Cuidador")

        with st.form("form_cuidador"):
            nome = st.text_input("Nome")
            telefone = st.text_input("Telefone (opcional)")
            cor = st.color_picker("Cor", "#3498db")

            if st.form_submit_button("Adicionar"):
                if nome:
                    novo = Cuidador(
                        id=str(uuid.uuid4())[:8],
                        nome=nome,
                        telefone=telefone or None,
                        cor=cor,
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