from scheme import *
import requests
import re

def obter_html_cardapio()->str:
    resp=requests.get("https://www.puspsc.usp.br/cardapio/")
    if resp.status_code != 200:
        raise Exception("Erro ao obter o cardápio")
    return resp.text


def parsing_cardapio(html:str)->tuple[list[RefeicaoRegistro],list[RefeicaoIndisponivel]]:
    dias_da_semana= [
        "Segunda-feira",
        "Terça-feira",
        "Quarta-feira",
        "Quinta-feira",
        "Sexta-feira",
        "Sábado",
    ]
    match_data_inicial=re.findall(r"\d{2}/\d{2}/\d{4}\s*a\s*\d{2}/\d{2}/\d{4}",html)
    if len(match_data_inicial) != 1:
        raise Exception("Formato de data inicial/final inválido no cardápio")
    data_inicio = datetime.datetime.strptime(match_data_inicial[0][:10], "%d/%m/%Y").date()
    refeicao_registros:list[RefeicaoRegistro]=[]
    refeicao_indisponiveis:list[RefeicaoIndisponivel]=[]
    for offset,dia in enumerate(dias_da_semana):
        data_refeicao=data_inicio + datetime.timedelta(days=offset)
        padrao = rf"{dia}.*?Mini Pão e Suco"
        matches = re.findall(padrao, html, flags=re.DOTALL)
        if not matches:
            refeicao_indisponiveis.append(RefeicaoIndisponivel(data_refeicao=data_refeicao, tipo_refeicao=TipoRefeicao.ALMOCO))
            continue
        tabela=matches[0].replace("\n", "").split("<br />")[1:-1]
        sobremesa_a,sobremesa_b = tabela[-1].replace("Sobremesa: ","").rsplit(r"/",1)
        refeicao_registros.append(RefeicaoRegistro(
            data_refeicao= data_refeicao,
            tipo_refeicao=TipoRefeicao.ALMOCO,
            principal=tabela[0],
            vegetariano=tabela[1].replace("Opção do Prato Principal: ", ""),
            guarnicao=tabela[2],
            sobremesa_opcao1=sobremesa_a,
            sobremesa_opcao2=sobremesa_b
        ))
    return. (refeicao_registros,refeicao_indisponiveis)


parsing_cardapio(obter_html_cardapio())