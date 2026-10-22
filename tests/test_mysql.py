"""Integração real em MySQL; exige opt-in e banco com sufixo _test."""
import os
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from database import get_engine, get_session
from main import app
from models import Aluno, Curso, Matricula, Nota, Professor, Turma

pytestmark = pytest.mark.skipif(os.getenv('RUN_MYSQL_TESTS') != '1', reason='Configure um MySQL de teste e RUN_MYSQL_TESTS=1.')


@pytest.fixture
def session():
    engine = get_engine()
    assert engine.url.database.endswith('_test'), 'Use um banco descartável com sufixo _test.'
    with engine.connect() as connection:
        outer = connection.begin()
        with Session(bind=connection, join_transaction_mode='create_savepoint', expire_on_commit=False) as db:
            yield db
        outer.rollback()


@pytest.fixture
def client(session):
    def override():
        yield session
    app.dependency_overrides[get_session] = override
    with TestClient(app) as browser:
        yield browser
    app.dependency_overrides.clear()


def test_full_relational_chain(session):
    aluno = Aluno(nome_aluno='Teste ORM', data_nascimento=date(2007, 1, 1), email_aluno='orm@example.com', telefone_aluno='11999999999')
    professor = Professor(nome_professor='Teste ORM', email_professor='orm@example.com', telefone_professor='11999999998', especialidade_professor='Testes')
    curso = Curso(nome_curso='Teste ORM', descricao_curso='Teste', cargahoraria_curso=80)
    session.add_all([aluno, professor, curso])
    session.flush()
    turma = Turma(curso=curso, professor=professor, ano_letivo=2026, semestre_turma=2, turno_turma='manhã')
    session.add(turma)
    session.flush()
    matricula = Matricula(aluno=aluno, turma=turma, data_matricula=date(2026, 10, 22), situacao_matricula='ativa')
    session.add(matricula)
    session.flush()
    for value in ('0.00', '8.50', '10.00'):
        session.add(Nota(matricula=matricula, descricao_nota='Avaliação', valor_nota=Decimal(value), data_nota=date(2026, 10, 22)))
    session.flush()
    assert matricula.aluno.nome_aluno == 'Teste ORM'
    assert turma.professor is professor
    assert session.scalar(select(func.count(Nota.id_nota)).where(Nota.id_matricula == matricula.id_matricula)) == 3
    assert abs(session.scalar(select(func.avg(Nota.valor_nota)).where(Nota.id_matricula == matricula.id_matricula)) - Decimal('18.5') / 3) < Decimal('.0001')
    assert session.execute(text('SELECT * FROM vw_alunos_cursos_turmas WHERE nome_aluno=:nome'), {'nome': 'Teste ORM'}).first()
    aluno.nome_aluno = 'Atualizado'
    session.flush()
    assert session.scalar(select(Aluno.nome_aluno).where(Aluno.id_aluno == aluno.id_aluno)) == 'Atualizado'

    # SAVEPOINT permite verificar erros sem perder a cadeia do teste.
    statements = [
        ("INSERT INTO aluno(nome_aluno,data_nascimento,email_aluno,telefone_aluno) VALUES ('Duplicado','2007-01-01','orm@example.com','11999999999')", {}),
        ("INSERT INTO professor(nome_professor,email_professor,telefone_professor,especialidade_professor) VALUES ('Duplicado','orm@example.com','11999999999','Teste')", {}),
        ("INSERT INTO matricula(id_aluno,id_turma,data_matricula,situacao_matricula) VALUES (:aluno,:turma,'2026-10-22','ativa')", {'aluno': aluno.id_aluno, 'turma': turma.id_turma}),
        ("INSERT INTO turma(id_curso,id_professor,ano_letivo,semestre_turma,turno_turma) VALUES (-1,:professor,2026,2,'manhã')", {'professor': professor.id_professor}),
        ("INSERT INTO curso(nome_curso,descricao_curso,cargahoraria_curso) VALUES ('Inválido','Teste',0)", {}),
    ]
    for grade in ('-0.01', '10.01'):
        statements.append(("INSERT INTO nota(id_matricula,descricao_nota,valor_nota,data_nota) VALUES (:id,'Inválida',:valor,'2026-10-22')", {'id': matricula.id_matricula, 'valor': grade}))
    for model, record in [(Aluno, aluno), (Professor, professor), (Curso, curso), (Turma, turma), (Matricula, matricula)]:
        pk = next(iter(model.__table__.primary_key.columns)).name
        statements.append((f'DELETE FROM {model.__tablename__} WHERE {pk}=:id', {'id': getattr(record, pk)}))
    for sql, params in statements:
        with pytest.raises(DBAPIError) as caught:
            with session.begin_nested():
                session.execute(text(sql), params)
        assert caught.value.orig.args[0] in (1062, 1451, 1452, 3819)
    for note in list(matricula.notas):
        session.delete(note)
    session.flush()
    for record in (matricula, turma, curso, professor, aluno):
        session.delete(record)
        session.flush()


def test_routes_reports_and_private_files(client):
    assert client.get('/').status_code == 200
    for page in ('alunos', 'professores', 'cursos', 'turmas', 'matriculas', 'notas'):
        assert client.get('/' + page).status_code == 200
        assert client.get('/' + page + '/cadastrar').status_code == 200
        assert client.get('/' + page + '/999999999').status_code == 404
    for report in ('alunos', 'professores', 'cursos', 'turma', 'notas', 'medias', 'quantidade', 'situacao', 'view'):
        assert client.get('/relatorios', params={'report': report}).status_code == 200
    assert client.get('/docs').status_code == 200
    assert len(client.get('/openapi.json').json()['paths']) == 32
    for path in ('/.env', '/.git/config', '/database.py', '/sql/seed.sql', '/templates/base.html'):
        assert client.get(path).status_code == 404


def test_invalid_requests_and_csrf(client):
    before = client.get('/alunos').text
    assert client.post('/alunos/cadastrar', data={'nome_aluno': 'Sem token'}).status_code == 403
    assert client.post('/alunos/cadastrar', data={'csrf': '♡'}).status_code == 403
    assert client.get('/alunos?p=texto').status_code == 422
    assert client.get('/alunos/-1').status_code == 422
    assert client.get('/alunos/1/editar').status_code == 200
    assert client.get('/alunos/1/excluir').status_code == 200
    assert client.get('/alunos').text == before


def test_empty_states(client, session):
    for table in ('nota', 'matricula', 'turma', 'curso', 'professor', 'aluno'):
        session.execute(text(f'DELETE FROM {table}'))
    assert 'Ainda não há matrículas' in client.get('/').text
    assert 'Nenhum registro encontrado' in client.get('/alunos').text
    assert 'Nenhum resultado' in client.get('/relatorios').text
    assert 'Cadastre cursos' in client.get('/turmas/cadastrar').text
