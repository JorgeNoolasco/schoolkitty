"""Mapeamento do esquema existente, sem executar create_all na aplicação."""
from datetime import date
from decimal import Decimal

from sqlalchemy import CHAR, CheckConstraint, Date, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Aluno(Base):
    __tablename__ = 'aluno'
    __table_args__ = (UniqueConstraint('email_aluno', name='uq_aluno_email'),
                      Index('idx_aluno_nome', 'nome_aluno'))
    id_aluno: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome_aluno: Mapped[str] = mapped_column(String(100))
    data_nascimento: Mapped[date] = mapped_column(Date)
    email_aluno: Mapped[str] = mapped_column(String(100))
    telefone_aluno: Mapped[str] = mapped_column(CHAR(11))
    matriculas: Mapped[list['Matricula']] = relationship(back_populates='aluno', passive_deletes='all')


class Professor(Base):
    __tablename__ = 'professor'
    __table_args__ = (UniqueConstraint('email_professor', name='uq_professor_email'),
                      Index('idx_professor_nome', 'nome_professor'),
                      Index('idx_professor_especialidade', 'especialidade_professor'))
    id_professor: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome_professor: Mapped[str] = mapped_column(String(100))
    email_professor: Mapped[str] = mapped_column(String(100))
    telefone_professor: Mapped[str] = mapped_column(CHAR(11))
    especialidade_professor: Mapped[str] = mapped_column(String(100))
    turmas: Mapped[list['Turma']] = relationship(back_populates='professor', passive_deletes='all')


class Curso(Base):
    __tablename__ = 'curso'
    __table_args__ = (CheckConstraint('cargahoraria_curso > 0', name='ck_curso_horas'),)
    id_curso: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome_curso: Mapped[str] = mapped_column(String(100))
    descricao_curso: Mapped[str] = mapped_column(String(100))
    cargahoraria_curso: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    turmas: Mapped[list['Turma']] = relationship(back_populates='curso', passive_deletes='all')


class Turma(Base):
    __tablename__ = 'turma'
    __table_args__ = (
        CheckConstraint('ano_letivo BETWEEN 1900 AND 2100', name='ck_turma_ano'),
        CheckConstraint('semestre_turma IN (1,2)', name='ck_turma_semestre'),
        CheckConstraint("turno_turma IN ('manhã','tarde','noite')", name='ck_turma_turno'),
    )
    id_turma: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_curso: Mapped[int] = mapped_column(ForeignKey('curso.id_curso', name='fk_turma_curso', ondelete='RESTRICT', onupdate='RESTRICT'))
    id_professor: Mapped[int] = mapped_column(ForeignKey('professor.id_professor', name='fk_turma_professor', ondelete='RESTRICT', onupdate='RESTRICT'))
    ano_letivo: Mapped[int] = mapped_column(Integer)
    semestre_turma: Mapped[int] = mapped_column(Integer)
    turno_turma: Mapped[str] = mapped_column(String(20))
    curso: Mapped[Curso] = relationship(back_populates='turmas')
    professor: Mapped[Professor] = relationship(back_populates='turmas')
    matriculas: Mapped[list['Matricula']] = relationship(back_populates='turma', passive_deletes='all')


class Matricula(Base):
    __tablename__ = 'matricula'
    __table_args__ = (
        UniqueConstraint('id_aluno', 'id_turma', name='uq_matricula_aluno_turma'),
        CheckConstraint("situacao_matricula IN ('ativa','concluída','cancelada','trancada')", name='ck_matricula_situacao'),
        Index('idx_matricula_data', 'data_matricula'),
        Index('idx_matricula_situacao', 'situacao_matricula'),
    )
    id_matricula: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_aluno: Mapped[int] = mapped_column(ForeignKey('aluno.id_aluno', name='fk_matricula_aluno', ondelete='RESTRICT', onupdate='RESTRICT'))
    id_turma: Mapped[int] = mapped_column(ForeignKey('turma.id_turma', name='fk_matricula_turma', ondelete='RESTRICT', onupdate='RESTRICT'))
    data_matricula: Mapped[date] = mapped_column(Date)
    situacao_matricula: Mapped[str] = mapped_column(String(20))
    aluno: Mapped[Aluno] = relationship(back_populates='matriculas')
    turma: Mapped[Turma] = relationship(back_populates='matriculas')
    notas: Mapped[list['Nota']] = relationship(back_populates='matricula', passive_deletes='all')


class Nota(Base):
    __tablename__ = 'nota'
    __table_args__ = (CheckConstraint('valor_nota BETWEEN 0 AND 10', name='ck_nota_valor'),)
    id_nota: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_matricula: Mapped[int] = mapped_column(ForeignKey('matricula.id_matricula', name='fk_nota_matricula', ondelete='RESTRICT', onupdate='RESTRICT'))
    descricao_nota: Mapped[str] = mapped_column(String(100))
    valor_nota: Mapped[Decimal] = mapped_column(Numeric(4, 2))
    data_nota: Mapped[date] = mapped_column(Date)
    matricula: Mapped[Matricula] = relationship(back_populates='notas')
