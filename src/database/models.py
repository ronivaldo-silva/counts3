from typing import List, Optional
from datetime import date, datetime

from sqlalchemy import String, Float, Boolean, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .config import Base

class Usuario(Base):
    """
    Tabela de usuários:
    * Deleted: Não é considerando em login ou transações mas em relatórios
    * Actived: Não é considerando em login mas em transações e relatórios
    """
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    senha: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    actived: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    creado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    registros: Mapped[List["Registro"]] = relationship("Registro", back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario(cpf={self.cpf}, nome={self.nome})>"

class Categoria(Base):
    """
    Tabela de categorias:
    * Repete: Se a categoria se repete mensalmente
    """
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    repete: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    registros: Mapped[List["Registro"]] = relationship("Registro", back_populates="categoria_rel")

    def __repr__(self):
        return f"<Categoria(nome={self.categoria})>"

class Classificacao(Base):
    __tablename__ = "classificacoes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    classificacao: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Classificacao(nome={self.classificacao})>"

class Registro(Base):
    __tablename__ = "registros"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    type_id: Mapped[int] = mapped_column(nullable=False) # 0 or 1
    category_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)
    
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    data_debito: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    data_entrada: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    data_prevista: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    creado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # New Columns for Debt Abatement
    classificacao_id: Mapped[int] = mapped_column(ForeignKey("classificacoes.id"), default=1)
    saldo: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="registros")
    categoria_rel: Mapped["Categoria"] = relationship("Categoria", back_populates="registros")
    classificacao_rel: Mapped["Classificacao"] = relationship("Classificacao")

    def __repr__(self):
        return f"<Registro(id={self.id}, valor={self.valor}, type_id={self.type_id})>"
        