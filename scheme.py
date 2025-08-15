from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String
import datetime
from enum import Enum

class TipoRefeicao(str, Enum):
    ALMOCO = "almoco"
    JANTAR = "jantar"


class DataBase(DeclarativeBase):
    def __repr__(self):
        attrs = []
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            attrs.append(f"{column.name}={val!r}")
        return f"<{self.__class__.__name__}({', '.join(attrs)})>"

class RefeicaoRegistro(DataBase):
    __tablename__ = "cardapios"
    data_refeicao: Mapped[datetime.date] = mapped_column(DateTime, primary_key=True)
    tipo_refeicao: Mapped[TipoRefeicao] = mapped_column(String(6), primary_key=True)
    principal: Mapped[str] = mapped_column(String(100), nullable=False)
    vegetariano: Mapped[str] = mapped_column(String(100), nullable=False)
    guarnicao: Mapped[str] = mapped_column(String(100), nullable=False)
    sobremesa_opcao1: Mapped[str] = mapped_column(String(100), nullable=False)
    sobremesa_opcao2: Mapped[str] = mapped_column(String(100), nullable=False)

