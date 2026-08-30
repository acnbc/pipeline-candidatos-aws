import pandas as pd

from src.gold import (
    agregar_cruzamento_genero_raca,
    agregar_patrimonio_candidato,
    agregar_representatividade_cargo,
)


def test_representatividade_cargo_pct_mulheres():
    dim = pd.DataFrame(
        {
            "sq_candidato": ["1", "2", "3", "4"],
            "codigo_cargo": ["6", "6", "6", "6"],
            "cargo": ["DEPUTADO FEDERAL"] * 4,
            "genero": ["FEMININO", "FEMININO", "MASCULINO", "MASCULINO"],
            "cor_raca": ["BRANCA", "PRETA", "BRANCA", "PARDA"],
            "faixa": ["18-29", "40-49", "50-59", "30-39"],
            "escolaridade": ["SUPERIOR COMPLETO"] * 4,
            "uf_nascimento": ["RJ", "RJ", "SP", "RJ"],
            "ST_QUILOMBOLA": ["N", "N", "N", "N"],
            "idade_data_de_posse": [25.0, 45.0, 55.0, 35.0],
        }
    )
    tabela = agregar_representatividade_cargo(dim)
    linha = tabela.iloc[0]
    assert linha["pct_mulheres"] == 50.0
    assert linha["lista_proporcional"] == True
    assert linha["qtd_candidatos"] == 4


def test_cruzamento_soma_100():
    dim = pd.DataFrame(
        {
            "sq_candidato": ["1", "2"],
            "genero": ["FEMININO", "MASCULINO"],
            "cor_raca": ["BRANCA", "PRETA"],
        }
    )
    tabela = agregar_cruzamento_genero_raca(dim)
    assert tabela["pct_do_total"].sum() == 100.0
    assert len(tabela) == 2


def test_quem_nao_tem_bem_fica_nan_nao_zero():
    dim = pd.DataFrame(
        {
            "sq_candidato": ["1", "2"],
            "nome_civil": ["Ana", "Bruno"],
            "nome_urna": ["Ana", "Bruno"],
            "cargo": ["GOVERNADOR", "GOVERNADOR"],
            "sigla_partido": ["X", "Y"],
            "ST_DECLARAR_BENS": ["S", "N"],
            "codigo_cargo": ["3", "3"],
            "genero": ["FEMININO", "MASCULINO"],
            "cor_raca": ["BRANCA", "PRETA"],
            "escolaridade": ["SUPERIOR COMPLETO", "ENSINO MÉDIO COMPLETO"],
            "ocupacao": ["ADVOGADO", "OUTROS"],
            "faixa": ["40-49", "50-59"],
            "idade_data_de_posse": [45.0, 52.0],
            "uf_nascimento": ["RJ", "SP"],
            "ST_QUILOMBOLA": ["N", "N"],
        }
    )
    bens = pd.DataFrame(
        {
            "sq_candidato": ["1", "1"],
            "valor_bem": [100.0, 50.0],
        }
    )

    tabela = agregar_patrimonio_candidato(dim, bens)
    da_ana = tabela.loc[tabela["sq_candidato"] == "1"].iloc[0]
    do_bruno = tabela.loc[tabela["sq_candidato"] == "2"].iloc[0]

    assert da_ana["patrimonio_total"] == 150.0
    assert da_ana["qtd_bens"] == 2
    assert pd.isna(do_bruno["patrimonio_total"])
    assert do_bruno["qtd_bens"] == 0