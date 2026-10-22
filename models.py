"""Mapeamento do esquema existente, sem executar create_all na aplicação."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
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


class Usuario(Base):
    """Conta de acesso associada a um aluno ou professor existente."""
    __tablename__ = 'usuario'
    __table_args__ = (
        CheckConstraint("perfil IN ('administrador','professor','aluno')", name='ck_usuario_perfil'),
        CheckConstraint('(perfil = \'administrador\' AND id_aluno IS NULL AND id_professor IS NULL) OR '
                        '(perfil = \'aluno\' AND id_aluno IS NOT NULL AND id_professor IS NULL) OR '
                        '(perfil = \'professor\' AND id_professor IS NOT NULL AND id_aluno IS NULL)',
                        name='ck_usuario_vinculo_perfil'),
        UniqueConstraint('id_aluno', name='uq_usuario_aluno'),
        UniqueConstraint('id_professor', name='uq_usuario_professor'),
    )
    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(20))
    id_aluno: Mapped[int | None] = mapped_column(ForeignKey('aluno.id_aluno', ondelete='RESTRICT'))
    id_professor: Mapped[int | None] = mapped_column(ForeignKey('professor.id_professor', ondelete='RESTRICT'))
    ativo: Mapped[int] = mapped_column(Integer, default=1)
    criado_em: Mapped[datetime] = mapped_column(DateTime)


class Atividade(Base):
    __tablename__ = 'atividade'
    __table_args__ = (CheckConstraint('pontuacao_maxima > 0 AND pontuacao_maxima <= 1000', name='ck_atividade_pontos'),
                      Index('idx_atividade_entrega', 'id_turma', 'data_entrega'))
    id_atividade: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_turma: Mapped[int] = mapped_column(ForeignKey('turma.id_turma', ondelete='RESTRICT'))
    id_professor: Mapped[int] = mapped_column(ForeignKey('professor.id_professor', ondelete='RESTRICT'))
    titulo: Mapped[str] = mapped_column(String(150))
    descricao: Mapped[str] = mapped_column(Text)
    instrucoes: Mapped[str] = mapped_column(Text)
    publicada_em: Mapped[datetime] = mapped_column(DateTime)
    data_entrega: Mapped[datetime] = mapped_column(DateTime)
    pontuacao_maxima: Mapped[Decimal] = mapped_column(Numeric(7, 2))


class EntregaAtividade(Base):
    __tablename__ = 'entrega_atividade'
    __table_args__ = (UniqueConstraint('id_atividade', 'id_aluno', name='uq_entrega_atividade_aluno'),
                      CheckConstraint('nota IS NULL OR nota >= 0', name='ck_entrega_nota_nao_negativa'))
    id_entrega: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_atividade: Mapped[int] = mapped_column(ForeignKey('atividade.id_atividade', ondelete='RESTRICT'))
    id_aluno: Mapped[int] = mapped_column(ForeignKey('aluno.id_aluno', ondelete='RESTRICT'))
    resposta: Mapped[str] = mapped_column(Text)
    entregue_em: Mapped[datetime] = mapped_column(DateTime)
    nota: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    feedback: Mapped[str | None] = mapped_column(Text)
    avaliada_em: Mapped[datetime | None] = mapped_column(DateTime)


class Aviso(Base):
    __tablename__ = 'aviso'
    __table_args__ = (Index('idx_aviso_turma_data', 'id_turma', 'publicado_em'),)
    id_aviso: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_turma: Mapped[int] = mapped_column(ForeignKey('turma.id_turma', ondelete='RESTRICT'))
    id_professor: Mapped[int] = mapped_column(ForeignKey('professor.id_professor', ondelete='RESTRICT'))
    titulo: Mapped[str] = mapped_column(String(150))
    mensagem: Mapped[str] = mapped_column(Text)
    publicado_em: Mapped[datetime] = mapped_column(DateTime)


class EventoCalendario(Base):
    __tablename__ = 'evento_calendario'
    __table_args__ = (Index('idx_evento_data', 'inicio_em'),)
    id_evento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_turma: Mapped[int | None] = mapped_column(ForeignKey('turma.id_turma', ondelete='RESTRICT'))
    id_criador: Mapped[int] = mapped_column(ForeignKey('usuario.id_usuario', ondelete='RESTRICT'))
    titulo: Mapped[str] = mapped_column(String(150))
    descricao: Mapped[str | None] = mapped_column(Text)
    inicio_em: Mapped[datetime] = mapped_column(DateTime)
    fim_em: Mapped[datetime | None] = mapped_column(DateTime)
