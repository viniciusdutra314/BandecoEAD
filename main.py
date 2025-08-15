from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String
import datetime
from enum import Enum

class TipoRefeicao(str, Enum):
    ALMOCO = "almoco"
    JANTAR = "jantar"

class DataBase(DeclarativeBase):
    pass

class RefeicaoRegistro(DataBase):
    __tablename__ = "cardapios"
    data_refeicao: Mapped[datetime.date] = mapped_column(DateTime, primary_key=True)
    tipo_refeicao: Mapped[TipoRefeicao] = mapped_column(String(6), primary_key=True)
    principal: Mapped[str] = mapped_column(String, nullable=False)
    vegetariano: Mapped[str] = mapped_column(String, nullable=False)
    guarnicao: Mapped[str] = mapped_column(String, nullable=False)
    sobremesa_opcao1: Mapped[str] = mapped_column(String, nullable=False)
    sobremesa_opcao2: Mapped[str] = mapped_column(String, nullable=False)


class RefeicaoIndisponivel(DataBase):
    __tablename__ = "refeicoes_indisponiveis"
    data_refeicao: Mapped[datetime.date] = mapped_column(DateTime, primary_key=True)
    tipo_refeicao: Mapped[TipoRefeicao] = mapped_column(String(16), primary_key=True)


