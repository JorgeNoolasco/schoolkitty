"""Metadados internos para compartilhar telas sem duplicar regras dos módulos."""
from dataclasses import dataclass

import models
import schemas


@dataclass(frozen=True)
class Field:
    label: str
    kind: str = 'text'
    relation: str | None = None
    options: tuple = ()


@dataclass(frozen=True)
class Entity:
    model: type
    schema: type
    pk: str
    title: str
    single: str
    icon: str
    fields: dict[str, Field]


ENTITIES = {
    'alunos': Entity(models.Aluno, schemas.AlunoSchema, 'id_aluno', 'Alunos', 'aluno', '♧', {
        'nome_aluno': Field('Nome completo'), 'data_nascimento': Field('Data de nascimento', 'date'),
        'email_aluno': Field('E-mail', 'email'), 'telefone_aluno': Field('Telefone com DDD', 'tel'),
    }),
    'professores': Entity(models.Professor, schemas.ProfessorSchema, 'id_professor', 'Professores', 'professor', '✧', {
        'nome_professor': Field('Nome completo'), 'email_professor': Field('E-mail', 'email'),
        'telefone_professor': Field('Telefone com DDD', 'tel'), 'especialidade_professor': Field('Especialidade'),
    }),
    'cursos': Entity(models.Curso, schemas.CursoSchema, 'id_curso', 'Cursos', 'curso', '▤', {
        'nome_curso': Field('Nome do curso'), 'descricao_curso': Field('Descrição'),
        'cargahoraria_curso': Field('Carga horária (horas)', 'hours'),
    }),
    'turmas': Entity(models.Turma, schemas.TurmaSchema, 'id_turma', 'Turmas', 'turma', '▦', {
        'id_curso': Field('Curso', 'relation', 'cursos'), 'id_professor': Field('Professor', 'relation', 'professores'),
        'ano_letivo': Field('Ano letivo', 'year'), 'semestre_turma': Field('Semestre', 'select', options=('1', '2')),
        'turno_turma': Field('Turno', 'select', options=('manhã', 'tarde', 'noite')),
    }),
    'matriculas': Entity(models.Matricula, schemas.MatriculaSchema, 'id_matricula', 'Matrículas', 'matrícula', '♡', {
        'id_aluno': Field('Aluno', 'relation', 'alunos'), 'id_turma': Field('Turma', 'relation', 'turmas'),
        'data_matricula': Field('Data de matrícula', 'date'),
        'situacao_matricula': Field('Situação', 'select', options=('ativa', 'concluída', 'cancelada', 'trancada')),
    }),
    'notas': Entity(models.Nota, schemas.NotaSchema, 'id_nota', 'Notas', 'nota', '☆', {
        'id_matricula': Field('Matrícula', 'relation', 'matriculas'), 'descricao_nota': Field('Avaliação'),
        'valor_nota': Field('Nota (0 a 10)', 'grade'), 'data_nota': Field('Data da avaliação', 'date'),
    }),
}
