# src/escala_vovo/infrastructure/repository.py
"""Persistência de dados em JSON"""

import json
from pathlib import Path
from datetime import date, time
from typing import List, Dict, Any, Optional
from ..core.models import Cuidador, Turno


class Repository:
    """Gerencia a persistência em JSON"""

    def __init__(self, arquivo: str = "data/escala.json"):
        self.arquivo = Path(arquivo)
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        self._dados = self._carregar()

    def _carregar(self) -> Dict[str, Any]:
        """Carrega dados do arquivo"""
        if self.arquivo.exists():
            try:
                with open(self.arquivo, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {"cuidadores": [], "turnos": []}
        return {"cuidadores": [], "turnos": []}

    def _salvar(self):
        """Salva dados no arquivo"""
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(self._dados, f, indent=2, ensure_ascii=False)

    # ============================================
    # CUIDADORES
    # ============================================

    def adicionar_cuidador(self, cuidador: Cuidador):
        """Adiciona um cuidador"""
        self._dados["cuidadores"].append({
            "id": cuidador.id,
            "nome": cuidador.nome,
            "telefone": cuidador.telefone,
            "cor": cuidador.cor,
            "ativo": cuidador.ativo,
            "pode_sabado": cuidador.pode_sabado,
            "pode_domingo": cuidador.pode_domingo,
        })
        self._salvar()

    def listar_cuidadores(self) -> List[Dict]:
        """Lista todos os cuidadores"""
        return self._dados.get("cuidadores", [])

    def listar_cuidadores_ativos(self) -> List[Dict]:
        """Lista apenas cuidadores ativos"""
        return [c for c in self.listar_cuidadores() if c.get("ativo", True)]

    def buscar_cuidador(self, cuidador_id: str) -> Optional[Dict]:
        """Busca um cuidador por ID"""
        for c in self.listar_cuidadores():
            if c["id"] == cuidador_id:
                return c
        return None

    def remover_cuidador(self, cuidador_id: str):
        """Remove um cuidador e seus turnos"""
        self._dados["cuidadores"] = [
            c for c in self._dados["cuidadores"] if c["id"] != cuidador_id
        ]
        self._dados["turnos"] = [
            t for t in self._dados["turnos"] if t["cuidador_id"] != cuidador_id
        ]
        self._salvar()

    def atualizar_cuidador(self, cuidador_id: str, **campos):
        """Atualiza campos de um cuidador"""
        for c in self._dados["cuidadores"]:
            if c["id"] == cuidador_id:
                c.update(campos)
                break
        self._salvar()

    # ============================================
    # TURNOS
    # ============================================

    def adicionar_turno(self, turno: Turno):
        """Adiciona um turno"""
        self._dados["turnos"].append({
            "id": turno.id,
            "data": turno.data.isoformat(),
            "cuidador_id": turno.cuidador_id,
            "hora_inicio": turno.hora_inicio.isoformat(),
            "hora_fim": turno.hora_fim.isoformat(),
            "observacoes": turno.observacoes,
        })
        self._salvar()

    def remover_turno(self, turno_id: str):
        """Remove um turno"""
        self._dados["turnos"] = [
            t for t in self._dados["turnos"] if t["id"] != turno_id
        ]
        self._salvar()

    def listar_turnos(self) -> List[Dict]:
        """Lista todos os turnos"""
        return self._dados.get("turnos", [])

    def listar_turnos_por_data(self, data_alvo: date) -> List[Dict]:
        """Lista turnos de uma data específica"""
        data_str = data_alvo.isoformat()
        return [t for t in self.listar_turnos() if t["data"] == data_str]

    def listar_turnos_por_cuidador(self, cuidador_id: str) -> List[Dict]:
        """Lista turnos de um cuidador"""
        return [t for t in self.listar_turnos() if t["cuidador_id"] == cuidador_id]

    def buscar_turno(self, turno_id: str) -> Optional[Dict]:
        """Busca um turno por ID"""
        for t in self.listar_turnos():
            if t["id"] == turno_id:
                return t
        return None

    def atualizar_turno(self, turno_id: str, nova_data: str = None,
                        cuidador_id: str = None, hora_inicio: str = None,
                        hora_fim: str = None):
        """
        Atualiza um turno (usado pelo drag-and-drop)

        Args:
            turno_id: ID do turno
            nova_data: Nova data no formato ISO (YYYY-MM-DD)
            cuidador_id: Novo cuidador
            hora_inicio: Nova hora de início (HH:MM)
            hora_fim: Nova hora de fim (HH:MM)
        """
        for t in self._dados["turnos"]:
            if t["id"] == turno_id:
                if nova_data:
                    t["data"] = nova_data
                if cuidador_id:
                    t["cuidador_id"] = cuidador_id
                if hora_inicio:
                    t["hora_inicio"] = hora_inicio
                if hora_fim:
                    t["hora_fim"] = hora_fim
                break
        self._salvar()

    def mover_turno(self, turno_id: str, nova_data: date):
        """Move um turno para outra data (drag-and-drop)"""
        self.atualizar_turno(turno_id, nova_data=nova_data.isoformat())

    # ============================================
    # UTILITÁRIOS
    # ============================================

    def to_turnos_model(self) -> List[Turno]:
        """Converte os turnos do JSON para objetos Turno"""
        turnos = []
        for t in self.listar_turnos():
            turnos.append(Turno(
                id=t["id"],
                data=date.fromisoformat(t["data"]),
                cuidador_id=t["cuidador_id"],
                hora_inicio=time.fromisoformat(t["hora_inicio"]),
                hora_fim=time.fromisoformat(t["hora_fim"]),
                observacoes=t.get("observacoes", ""),
            ))
        return turnos

    def limpar_tudo(self):
        """Limpa todos os dados (cuidado!)"""
        self._dados = {"cuidadores": [], "turnos": []}
        self._salvar()

    def estatisticas(self) -> Dict:
        """Retorna estatísticas do sistema"""
        return {
            "total_cuidadores": len(self.listar_cuidadores()),
            "cuidadores_ativos": len(self.listar_cuidadores_ativos()),
            "total_turnos": len(self.listar_turnos()),
        }