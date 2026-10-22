"""Operações ORM e consultas reais, sempre com parâmetros separados do SQL."""
from math import ceil

from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from entities import ENTITIES
from models import Aluno, Curso, Matricula, Nota, Professor, Turma
from queries import RELATION_QUERIES


def rows(session: Session, sql: str, parameters: dict | None = None) -> list[dict]:
    return [dict(row) for row in session.execute(text(sql), parameters or {}).mappings()]


def options(session: Session, key: str) -> dict[str, str]:
    return {str(row['id']): row['label'] for row in rows(session, RELATION_QUERIES[key])}


def get_record(session, entity, record_id):
    record = session.get(entity.model, record_id)
    if record is None:
        raise HTTPException(404, 'Registro não encontrado.')
    return record


def record_data(record, entity):
    return {name: getattr(record, name) for name in [entity.pk, *entity.fields]}


def listing(session, key, search='', specialty='', page=1):
    entity = ENTITIES[key]
    model = entity.model
    conditions = []
    if search:
        term = f'%{search}%'
        if key == 'matriculas':
            conditions.append(Matricula.id_aluno.in_(select(Aluno.id_aluno).where(Aluno.nome_aluno.like(term))))
        elif key == 'notas':
            conditions.append(Nota.id_matricula.in_(select(Matricula.id_matricula).join(Aluno).where(Aluno.nome_aluno.like(term))))
        elif key == 'turmas':
            conditions.append(Turma.id_curso.in_(select(Curso.id_curso).where(Curso.nome_curso.like(term))))
        else:
            conditions.append(getattr(model, next(iter(entity.fields))).like(term))
    if key == 'professores' and specialty:
        conditions.append(Professor.especialidade_professor == specialty)
    total = session.scalar(select(func.count()).select_from(model).where(*conditions))
    pages = max(1, ceil(total / 15))
    current = min(pages, max(1, page))
    statement = select(model).where(*conditions).order_by(getattr(model, entity.pk).desc()).limit(15).offset((current - 1) * 15)
    return {'records': [record_data(record, entity) for record in session.scalars(statement)],
            'total': total, 'pages': pages, 'current': current}


def validate_relations(session, entity, values):
    errors = []
    for name, field in entity.fields.items():
        if field.kind == 'relation' and session.get(ENTITIES[field.relation].model, values[name]) is None:
            errors.append(f'{field.label} não existe. Cadastre um registro antes de continuar.')
    return errors


def save(session, entity, values, record=None):
    if record is None:
        record = entity.model(**values)
        session.add(record)
    else:
        for name, value in values.items():
            setattr(record, name, value)
    # A confirmação é feita pelo controlador; falhas sempre provocam rollback.
    session.flush()
    return record


def dashboard(session):
    counts = {key: session.scalar(select(func.count()).select_from(entity.model))
              for key, entity in ENTITIES.items() if key != 'notas'}
    average = session.scalar(select(func.avg(Nota.valor_nota)))
    recent = rows(session, '''SELECT a.nome_aluno,c.nome_curso,t.id_turma,t.ano_letivo,
        t.semestre_turma,m.data_matricula,m.situacao_matricula,m.id_matricula
        FROM matricula m JOIN aluno a USING(id_aluno) JOIN turma t USING(id_turma)
        JOIN curso c USING(id_curso) ORDER BY m.data_matricula DESC,m.id_matricula DESC LIMIT 5''')
    return {'counts': counts, 'average': average, 'recent': recent}


def linked_records(session, key, record_id):
    title, result = 'Registros vinculados', []
    if key in ('professores', 'cursos'):
        # Apenas nomes internos permitidos entram na estrutura da consulta.
        column = {'professores': 'id_professor', 'cursos': 'id_curso'}[key]
        result = rows(session, f'''SELECT t.id_turma AS Turma,c.nome_curso AS Curso,
            p.nome_professor AS Professor,t.ano_letivo AS Ano,t.semestre_turma AS Semestre,
            t.turno_turma AS Turno FROM turma t JOIN curso c USING(id_curso)
            JOIN professor p USING(id_professor) WHERE t.{column} = :record_id''', {'record_id': record_id})
        title = 'Turmas associadas'
    elif key in ('alunos', 'turmas'):
        column = {'alunos': 'id_aluno', 'turmas': 'id_turma'}[key]
        result = rows(session, f'''SELECT m.id_matricula AS Matrícula,a.nome_aluno AS Aluno,
            c.nome_curso AS Curso,t.id_turma AS Turma,t.ano_letivo AS Ano,
            t.semestre_turma AS Semestre,t.turno_turma AS Turno,m.data_matricula AS Data,
            m.situacao_matricula AS Situação FROM matricula m JOIN aluno a USING(id_aluno)
            JOIN turma t USING(id_turma) JOIN curso c USING(id_curso)
            WHERE m.{column} = :record_id ORDER BY m.data_matricula DESC''', {'record_id': record_id})
        title = 'Histórico de matrículas'
    elif key == 'matriculas':
        result = rows(session, '''SELECT descricao_nota AS Avaliação,valor_nota AS Nota,data_nota AS Data
            FROM nota WHERE id_matricula = :record_id ORDER BY data_nota DESC''', {'record_id': record_id})
        average = session.scalar(select(func.avg(Nota.valor_nota)).where(Nota.id_matricula == record_id))
        title = 'Avaliações · Média: ' + (f'{average:.2f}'.replace('.', ',') if average is not None else 'sem notas')
    return {'linked': result, 'linked_title': title}
