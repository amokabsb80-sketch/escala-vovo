# src/escala_vovo/core/rules.py
"""Regras de negócio da escala"""

from datetime import date, timedelta
from typing import List, Tuple
from .models import Turno


class RegrasEscala:
    """Regras de validação da escala"""

    # Configurações (ajuste conforme a necessidade da sua avó)
    DIAS_DESCANSO_MINIMO = 0  # dias de descanso após um turno
    MAX_TURNOS_POR_SEMANA = 2  # máximo de turnos por semana por cuidador

    @classmethod
    def pode_alocar(cls, cuidador_id: str, data_alvo: date,
                    turnos_existentes: List[Turno]) -> Tuple[bool, str]:
        """
        Verifica se um cuidador pode ser alocado em uma data

        Returns:
            (pode_alocar, motivo)
        """
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
    def validar_turno(cls, turno: Turno) -> Tuple[bool, str]:
        """Valida um turno individual"""
        if turno.hora_fim <= turno.hora_inicio:
            return False, "Hora de fim deve ser maior que hora de início"
        return True, "OK"