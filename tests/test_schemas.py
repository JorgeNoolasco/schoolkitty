"""Validações sem depender de MySQL ou do navegador."""
from datetime import timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from schemas import AlunoSchema, CursoSchema, NotaSchema, TurmaSchema, today


def aluno(**changes):
    return AlunoSchema.model_validate(dict(nome_aluno='Ana', data_nascimento='2007-01-01',
        email_aluno='ana@example.com', telefone_aluno='(11) 99999-9999') | changes)


def test_phone_and_whitespace():
    value = aluno(nome_aluno='  Ana  ')
    assert value.nome_aluno == 'Ana'
    assert value.telefone_aluno == '11999999999'


@pytest.mark.parametrize('changes', [
    {'nome_aluno': ' '}, {'nome_aluno': 'á' * 101}, {'email_aluno': 'invalido'},
    {'telefone_aluno': 'abc11999999999'}, {'data_nascimento': '2026-02-30'},
    {'data_nascimento': '1234567890'}, {'data_nascimento': (today() + timedelta(days=1)).isoformat()},
])
def test_invalid_aluno(changes):
    with pytest.raises(ValidationError):
        aluno(**changes)


@pytest.mark.parametrize('value', ['0', '8,50', '10.00'])
def test_valid_grades(value):
    note = NotaSchema(id_matricula=1, descricao_nota='Avaliação', valor_nota=value, data_nota='2026-10-22')
    assert 0 <= note.valor_nota <= 10


@pytest.mark.parametrize('value', ['-0.01', '10.01', '1.234', 'NaN', 'Infinity', ''])
def test_invalid_grades(value):
    with pytest.raises(ValidationError):
        NotaSchema(id_matricula=1, descricao_nota='Avaliação', valor_nota=value, data_nota='2026-10-22')


def test_course_and_class_limits():
    assert CursoSchema(nome_curso='Curso', descricao_curso='Descrição', cargahoraria_curso='80,50').cargahoraria_curso == Decimal('80.50')
    with pytest.raises(ValidationError):
        CursoSchema(nome_curso='Curso', descricao_curso='Descrição', cargahoraria_curso=0)
    for changes in [{'id_curso': 0}, {'semestre_turma': 3}, {'turno_turma': 'madrugada'}, {'ano_letivo': 1800}]:
        with pytest.raises(ValidationError):
            TurmaSchema.model_validate(dict(id_curso=1, id_professor=1, ano_letivo=2026,
                semestre_turma=2, turno_turma='manhã') | changes)
