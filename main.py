from scheme import *
import requests
import sqlalchemy as sa
from sqlalchemy.orm import Session
import re

DIAS_DA_SEMANA = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo"
]

def obter_html_cardapio() -> str:
    resp = requests.get("https://www.puspsc.usp.br/cardapio/")
    if resp.status_code != 200:
        raise Exception("Erro ao obter o cardápio")
    return resp.text



def scrap_cardapio(html:str) -> list[RefeicaoRegistro]:
    match_data_inicial = re.findall(
        r"\d{2}/\d{2}/\d{4}\s*a\s*\d{2}/\d{2}/\d{4}", html)
    data_inicio = datetime.datetime.strptime(
        match_data_inicial[0][:10], "%d/%m/%Y").date()
    refeicao_registros: list[RefeicaoRegistro] = []
    for offset, dia in enumerate(DIAS_DA_SEMANA):
        data_refeicao = data_inicio + datetime.timedelta(days=offset)
        padrao = rf"{dia}.*?Mini Pão e Suco</td>\n</tr>"
        matches = re.findall(padrao, html, flags=re.DOTALL)
        if matches:
            submatches = re.findall(
                r"Saladas: Diversas.*?Mini Pão e Suco", matches[0], flags=re.DOTALL)
            for index, submatch in enumerate(submatches):
                tabela = submatch.replace("\n", "").split("<br />")[1:-1]
                sobremesa_a, sobremesa_b = tabela[-1].replace(
                    "Sobremesa: ", "").rsplit(r"/", 1)
                refeicao_registros.append(RefeicaoRegistro(
                    data_refeicao=data_refeicao,
                    tipo_refeicao=TipoRefeicao.ALMOCO if index == 0 else TipoRefeicao.JANTAR,
                    principal=tabela[0],
                    vegetariano=tabela[1].replace(
                        "Opção do Prato Principal: ", ""),
                    guarnicao=tabela[2],
                    sobremesa_opcao1=sobremesa_a,
                    sobremesa_opcao2=sobremesa_b
                ))

    return refeicao_registros

if __name__ == "__main__":
    refeicao_registros = scrap_cardapio(obter_html_cardapio())
    db_engine=sa.create_engine("sqlite:///bandeijao_usp_sao_carlos.db")
    DataBase.metadata.create_all(db_engine)
    with Session(db_engine) as session:
        try:
            for refeicao in refeicao_registros:
                session.add(refeicao)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Erro ao salvar no banco de dados: {e}")
            raise
    print("Cardápio atualizado com sucesso!")
