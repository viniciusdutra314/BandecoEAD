from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String,Date,Text
import datetime
from enum import Enum
import requests
import sqlalchemy as sa
from sqlalchemy.orm import Session
import re


class TipoRefeicao(str, Enum):
    ALMOCO = "almoco"
    JANTA = "janta"


class DataBase(DeclarativeBase):
    def __repr__(self):
        attrs = []
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            attrs.append(f"{column.name}={val!r}")
        return f"<{self.__class__.__name__}({', '.join(attrs)})>"

class RefeicaoRegistro(DataBase):
    __tablename__ = "cardapios"
    data_refeicao: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    tipo_refeicao: Mapped[TipoRefeicao] = mapped_column(String(6), primary_key=True)
    principal: Mapped[str] = mapped_column(String(100), nullable=False)
    vegetariano: Mapped[str] = mapped_column(String(100), nullable=False)
    guarnicao: Mapped[str] = mapped_column(String(100), nullable=False)
    sobremesa_opcao1: Mapped[str] = mapped_column(String(100), nullable=False)
    sobremesa_opcao2: Mapped[str] = mapped_column(String(100), nullable=False)

    def __str__(self) -> str:
        texto=""
        texto += f"Prato Principal: {self.principal}\n"
        texto += f"Opção Vegetariana: {self.vegetariano}\n"
        texto += f"Guarnição: {self.guarnicao}\n"
        texto += f"Sobremesa 1: {self.sobremesa_opcao1}\n"
        texto += f"Sobremesa 2: {self.sobremesa_opcao2}\n"
        return texto


def obter_html_cardapio() -> str:
    resp = requests.get("https://www.puspsc.usp.br/cardapio/")
    if resp.status_code != 200:
        raise Exception("Erro ao obter o cardápio")
    return resp.text


def scrap_cardapio(html: str) -> list[RefeicaoRegistro]:
    DIAS_DA_SEMANA = [
        "Segunda-feira",
        "Terça-feira",
        "Quarta-feira",
        "Quinta-feira",
        "Sexta-feira",
        "Sábado",
        "Domingo"
    ]
    match_data_inicial = re.findall(
        r"\d{2}/\d{2}/\d{4}\s*a\s*\d{2}/\d{2}/\d{4}", html)
    data_inicio = datetime.datetime.strptime(
        match_data_inicial[0][:10], "%d/%m/%Y").date()
    refeicao_registros: list[RefeicaoRegistro] = []
    for offset, dia in enumerate(DIAS_DA_SEMANA):
        data_refeicao = data_inicio + datetime.timedelta(days=offset)
        padrao = rf"{dia}.*?Mini Pão e Suco</td>\n</tr>"
        matches = re.findall(padrao, html, flags=re.DOTALL)
        raw_data = matches[0] if matches else ""
        if raw_data:
            submatches = re.findall(
                r"Saladas: Diversas.*?Mini Pão e Suco", raw_data, flags=re.DOTALL)
            for index, submatch in enumerate(submatches):
                tabela = submatch.replace("\n", "").split("<br />")[1:-1]
                sobremesa_a, sobremesa_b = tabela[-1].replace(
                    "Sobremesa: ", "").rsplit(r"/", 1)
                refeicao_registros.append(RefeicaoRegistro(
                    data_refeicao=data_refeicao,
                    tipo_refeicao=TipoRefeicao.ALMOCO if index == 0 else TipoRefeicao.JANTA,
                    principal=tabela[0],
                    vegetariano=tabela[1].replace(
                        "Opção do Prato Principal: ", ""),
                    guarnicao=tabela[2],
                    sobremesa_opcao1=sobremesa_a,
                    sobremesa_opcao2=sobremesa_b,
                ))
    return refeicao_registros


if __name__ == "__main__":
    refeicao_registros = scrap_cardapio(obter_html_cardapio())
    db_engine = sa.create_engine("sqlite:///../bandeijao_usp_sao_carlos.db")
    DataBase.metadata.create_all(db_engine)
    with Session(db_engine) as session:
        for refeicao in refeicao_registros:
                session.add(refeicao)
        session.commit()
        print("Cardápio atualizado com sucesso!")