import pandas as pd

from src.limpeza import (
    classificar_plataforma,
    faixa_etaria,
    parse_data_br,
    parse_real_br,
    parse_real_ponto,
)


def test_parse_real_br_converte_virgula():
    serie = pd.Series(["169292,43", "1.500,00"])
    obtido = parse_real_br(serie)
    assert obtido.iloc[0] == 169292.43
    assert obtido.iloc[1] == 1500.0


def test_parse_real_br_texto_vira_nan():
    obtido = parse_real_br(pd.Series(["abc"]))
    assert pd.isna(obtido.iloc[0])


def test_parse_real_ponto_nao_apaga_decimal():
    obtido = parse_real_ponto(pd.Series(["1270629.01"]))
    assert obtido.iloc[0] == 1270629.01


def test_parse_data_br_dia_primeiro():
    obtido = parse_data_br(pd.Series(["04/10/2026"]))
    assert obtido.iloc[0].day == 4
    assert obtido.iloc[0].month == 10


def test_parse_data_br_invalida_vira_nan():
    obtido = parse_data_br(pd.Series(["31/02/2026"]))
    assert pd.isna(obtido.iloc[0])


def test_plataforma_instagram_maiusculo():
    assert classificar_plataforma("HTTPS://WWW.INSTAGRAM.COM/FULANO") == "instagram"


def test_plataforma_sem_url():
    assert classificar_plataforma(None) == "sem_url"


def test_faixa_etaria_limites():
    assert faixa_etaria(29) == "18-29"
    assert faixa_etaria(30) == "30-39"
    assert faixa_etaria(None) is None