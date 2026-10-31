# src/escala_vovo/core/rules.py
"""Regras de negócio da escala"""

from datetime import date, timedelta
from typing import List, Tuple
from .models import Turno


class RegrasEscala:
    """Regras de validação da escala"""

    # Configurações (ajuste conforme a necessidade da sua avó)
    DIAS_DESCANSO_MINIMO = 0  # dias de descanso após um turno
    MAX_TURNOS_POR_SEMANA = 3  # máximo de turnos por semana por cuidador

    @classmethod
    def pode_alocar(cls, cuidador_id: str, data_alvo: date,
                    turnos_existentes: List[Turno],
                    cuidador: dict = None) -> Tuple[bool, str]:
        """
        Verifica se um cuidador pode ser alocado em uma data

        Args:
            cuidador_id: ID do cuidador
            data_alvo: Data a verificar
            turnos_existentes: Lista de turnos já cadastrados
            cuidador: Dicionário com dados do cuidador (opcional)

        Returns:
            (pode_alocar, motivo)
        """
        # 0. Verifica disponibilidade de fim de semana
        if cuidador:
            pode, motivo = cls.pode_trabalhar_no_dia(cuidador, data_alvo)
            if not pode:
                return False, motivo

        # 1. Verifica se já está alocado neste dia
        for turno in turnos_existentes:
            if turno.cuidador_id == cuidador_id and turno.data == data_alvo:
                return False, "Cuidador já está alocado neste dia"

        # 2. Verifica descanso mínimo
        data_anterior = data_alvo - timedelta(days=cls.DIAS_DESCANSO_MINIMO)
        for turno in turnos_existentes:
            if turno.cuidador_id == cuidador_id and turno.data == data_anterior:
                return False, (
                    f"Cuidador precisa de {cls.DIAS_DESCANSO_MINIMO} "
                    f"dia(s) de descanso"
                )

        # 3. Verifica máximo de turnos na semana
        inicio_semana = data_alvo - timedelta(days=data_alvo.weekday())
        fim_semana = inicio_semana + timedelta(days=6)

        turnos_semana = [
            t for t in turnos_existentes
            if t.cuidador_id == cuidador_id
               and inicio_semana <= t.data <= fim_semana
        ]

        if len(turnos_semana) >= cls.MAX_TURNOS_POR_SEMANA:
            return False, (
                f"Cuidador já tem {cls.MAX_TURNOS_POR_SEMANA} "
                f"turnos nesta semana"
            )

        return True, "OK"

    @classmethod
    def pode_trabalhar_no_dia(cls, cuidador: dict, data_alvo: date) -> Tuple[bool, str]:
        """
        Verifica se o cuidador pode trabalhar no dia da semana
        """
        dia_semana = data_alvo.weekday()  # 0=seg, 5=sáb, 6=dom

        if dia_semana == 5 and not cuidador.get("pode_sabado", True):
            return False, "Cuidador não trabalha aos sábados"

        if dia_semana == 6 and not cuidador.get("pode_domingo", True):
            return False, "Cuidador não trabalha aos domingos"

        return True, "OK"

    @classmethod
    def validar_turno(cls, turno: Turno) -> Tuple[bool, str]:
        """Valida um turno individual"""
        if turno.hora_fim <= turno.hora_inicio:
            return False, "Hora de fim deve ser maior que hora de início"
        return True, "OK"