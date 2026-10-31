# src/escala_vovo/infrastructure/supabase_repository.py
"""Persistência de dados no Supabase (PostgreSQL na nuvem)"""

import streamlit as st
from datetime import date, time
from typing import List, Dict, Optional
from ..core.models import Cuidador, Turno
from st_supabase_connection import SupabaseConnection


class SupabaseRepository:
    """Gerencia a persistência no Supabase"""

    def __init__(self):
        self.conn = st.connection("supabase", type=SupabaseConnection)

    # ============================================
    # CUIDADORES
    # ============================================

    def adicionar_cuidador(self, cuidador: Cuidador):
        self.conn.table("cuidadores").insert({
            "id": cuidador.id,
            "nome": cuidador.nome,
            "telefone": cuidador.telefone,
            "cor": cuidador.cor,
            "ativo": cuidador.ativo,
            "pode_sabado": cuidador.pode_sabado,
            "pode_domingo": cuidador.pode_domingo,
        }).execute()

    def listar_cuidadores(self) -> List[Dict]:
        response = self.conn.table("cuidadores").select("*").execute()
        return response.data if response.data else []

    def listar_cuidadores_ativos(self) -> List[Dict]:
        response = (
            self.conn.table("cuidadores")
            .select("*")
            .eq("ativo", True)
            .execute()
        )
        return response.data if response.data else []

    def buscar_cuidador(self, cuidador_id: str) -> Optional[Dict]:
        response = (
            self.conn.table("cuidadores")
            .select("*")
            .eq("id", cuidador_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def remover_cuidador(self, cuidador_id: str):
        # A FK com ON DELETE CASCADE já remove os turnos
        self.conn.table("cuidadores").delete().eq("id", cuidador_id).execute()

    def atualizar_cuidador(self, cuidador_id: str, **campos):
        self.conn.table("cuidadores").update(campos).eq("id", cuidador_id).execute()

    # ============================================
    # TURNOS
    # ============================================

    def adicionar_turno(self, turno: Turno):
        self.conn.table("turnos").insert({
            "id": turno.id,
            "data": turno.data.isoformat(),
            "cuidador_id": turno.cuidador_id,
            "hora_inicio": turno.hora_inicio.isoformat(),
            "hora_fim": turno.hora_fim.isoformat(),
            "observacoes": turno.observacoes,
        }).execute()

    def remover_turno(self, turno_id: str):
        self.conn.table("turnos").delete().eq("id", turno_id).execute()

    def listar_turnos(self) -> List[Dict]:
        response = self.conn.table("turnos").select("*").execute()
        return response.data if response.data else []

    def listar_turnos_por_data(self, data_alvo: date) -> List[Dict]:
        response = (
            self.conn.table("turnos")
            .select("*")
            .eq("data", data_alvo.isoformat())
            .execute()
        )
        return response.data if response.data else []

    def listar_turnos_por_cuidador(self, cuidador_id: str) -> List[Dict]:
        response = (
            self.conn.table("turnos")
            .select("*")
            .eq("cuidador_id", cuidador_id)
            .execute()
        )
        return response.data if response.data else []

    def buscar_turno(self, turno_id: str) -> Optional[Dict]:
        response = (
            self.conn.table("turnos")
            .select("*")
            .eq("id", turno_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def atualizar_turno(self, turno_id: str, nova_data: str = None,
                        cuidador_id: str = None, hora_inicio: str = None,
                        hora_fim: str = None):
        campos = {}
        if nova_data:
            campos["data"] = nova_data
        if cuidador_id:
            campos["cuidador_id"] = cuidador_id
        if hora_inicio:
            campos["hora_inicio"] = hora_inicio
        if hora_fim:
            campos["hora_fim"] = hora_fim
        if campos:
            self.conn.table("turnos").update(campos).eq("id", turno_id).execute()

    def mover_turno(self, turno_id: str, nova_data: date):
        self.atualizar_turno(turno_id, nova_data=nova_data.isoformat())

    # ============================================
    # UTILITÁRIOS
    # ============================================

    def to_turnos_model(self) -> List[Turno]:
        turnos = []
        for t in self.listar_turnos():
            turnos.append(Turno(
                id=t["id"],
                data=date.fromisoformat(t["data"]),
                cuidador_id=t["cuidador_id"],
                hora_inicio=time.fromisoformat(t["hora_inicio"]),
                hora_fim=time.fromisoformat(t["hora_fim"]),
                observacoes=t.get("observacoes", "") or "",
            ))
        return turnos

    def limpar_tudo(self):
        # Ordem importa: turnos primeiro (por causa da FK)
        self.conn.table("turnos").delete().neq("id", "").execute()
        self.conn.table("cuidadores").delete().neq("id", "").execute()

    def estatisticas(self) -> Dict:
        return {
            "total_cuidadores": len(self.listar_cuidadores()),
            "cuidadores_ativos": len(self.listar_cuidadores_ativos()),
            "total_turnos": len(self.listar_turnos()),
        }

    def listar_turnos_do_mes(self, ano: int, mes: int) -> List[Dict]:
        """Busca todos os turnos de um mês de uma vez (OTIMIZAÇÃO)"""
        from calendar import monthrange

        inicio = f"{ano}-{mes:02d}-01"
        ultimo_dia = monthrange(ano, mes)[1]
        fim = f"{ano}-{mes:02d}-{ultimo_dia:02d}"

        response = (
            self.conn.table("turnos")
            .select("*")
            .gte("data", inicio)
            .lte("data", fim)
            .execute()
        )
        return response.data if response.data else []