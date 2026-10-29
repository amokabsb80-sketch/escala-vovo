# src/escala_vovo/services/calendar_service.py
"""Serviço de geração de datas do calendário com dia da semana"""

from datetime import date
from typing import List, Tuple


class CalendarService:
    """
    Gera as datas do calendário conforme os períodos definidos:
    - Novembro e dezembro de 2026
    - Todo o ano de 2027
    """

    PERIODOS_VALIDOS = {
        2026: (date(2026, 11, 1), date(2026, 12, 31)),
        2027: (date(2027, 1, 1), date(2027, 12, 31)),
    }

    # Nomes dos dias da semana (0=segunda, 6=domingo)
    DIAS_SEMANA = [
        "Segunda-feira", "Terça-feira", "Quarta-feira",
        "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
    ]

    DIAS_SEMANA_CURTOS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    NOMES_MESES = [
        "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho", "Agosto",
        "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    @classmethod
    def get_anos_disponiveis(cls) -> List[int]:
        """Retorna a lista de anos disponíveis para seleção"""
        return sorted(cls.PERIODOS_VALIDOS.keys())

    @classmethod
    def get_periodo(cls, ano: int) -> Tuple[date, date]:
        """Retorna o período (início, fim) de um ano"""
        return cls.PERIODOS_VALIDOS.get(ano, (None, None))

    @classmethod
    def get_datas(cls, ano: int) -> List[date]:
        """Retorna todas as datas de um ano, dia a dia"""
        inicio, fim = cls.get_periodo(ano)
        if inicio is None:
            return []

        datas = []
        atual = inicio
        while atual <= fim:
            datas.append(atual)
            atual = date.fromordinal(atual.toordinal() + 1)

        return datas

    @classmethod
    def get_meses(cls, ano: int) -> List[Tuple[int, str]]:
        """Retorna os meses disponíveis no ano (número, nome)"""
        inicio, fim = cls.get_periodo(ano)
        if inicio is None:
            return []

        meses = []
        for mes in range(inicio.month, fim.month + 1):
            meses.append((mes, cls.NOMES_MESES[mes - 1]))

        return meses

    @classmethod
    def get_datas_do_mes(cls, ano: int, mes: int) -> List[date]:
        """Retorna todas as datas de um mês específico"""
        datas = cls.get_datas(ano)
        return [d for d in datas if d.month == mes]

    @classmethod
    def dia_semana(cls, data: date) -> str:
        """Retorna o dia da semana por extenso (ex: 'Segunda-feira')"""
        return cls.DIAS_SEMANA[data.weekday()]

    @classmethod
    def dia_semana_curto(cls, data: date) -> str:
        """Retorna o dia da semana abreviado (ex: 'Seg')"""
        return cls.DIAS_SEMANA_CURTOS[data.weekday()]

    @classmethod
    def formatar_data_completa(cls, data: date) -> str:
        """
        Retorna a data formatada por extenso
        Exemplo: 'Sábado, 15 de Novembro de 2026'
        """
        dia_semana = cls.dia_semana(data)
        mes = cls.NOMES_MESES[data.month - 1]
        return f"{dia_semana}, {data.day} de {mes} de {data.year}"

    @classmethod
    def formatar_data_curta(cls, data: date) -> str:
        """
        Retorna a data abreviada
        Exemplo: 'Sáb, 15/11/2026'
        """
        dia_semana = cls.dia_semana_curto(data)
        return f"{dia_semana}, {data.strftime('%d/%m/%Y')}"

    @classmethod
    def get_estrutura_mes(cls, ano: int, mes: int) -> List[dict]:
        """
        Retorna a estrutura completa do mês com dia da semana

        Returns:
            Lista de dicts com: data, dia, dia_semana, dia_semana_curto,
                                is_fim_semana
        """
        datas = cls.get_datas_do_mes(ano, mes)

        estrutura = []
        for d in datas:
            estrutura.append({
                'data': d,
                'dia': d.day,
                'mes': d.month,
                'ano': d.year,
                'dia_semana': cls.dia_semana(d),
                'dia_semana_curto': cls.dia_semana_curto(d),
                'is_fim_semana': d.weekday() >= 5,  # Sábado ou Domingo
                'data_formatada': cls.formatar_data_completa(d),
            })

        return estrutura