# src/escala_vovo/core/models.py
"""Modelos de dados do projeto"""

from dataclasses import dataclass, field
from datetime import date, time
from typing import List, Optional


@dataclass
class Cuidador:
    """Representa um cuidador"""
    id: str
    nome: str
    telefone: Optional[str] = None
    cor: str = "#3498db"  # cor para o calendário
    ativo: bool = True


@dataclass
class Turno:
    """Representa um turno de cuidado"""
    id: str
    data: date
    cuidador_id: str
    hora_inicio: time = time(8, 0)
    hora_fim: time = time(20, 0)
    observacoes: str = ""


@dataclass
class Escala:
    """Representa a escala completa"""
    cuidadores: List[Cuidador] = field(default_factory=list)
    turnos: List[Turno] = field(default_factory=list)