"""Controlador de formulários utilizado pelos seis módulos."""
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

import crud
from database import get_session
from entities import ENTITIES
from models import Professor
from schemas import today
from security import valid_csrf
from views import render, url

Database = Annotated[Session, Depends(get_session)]
RecordId = Annotated[int, Path(gt=0, le=2147483647)]


def error_messages(error, entity):
    messages = []
    for item in error.errors():
        name = item['loc'][0] if item['loc'] else ''
        field = entity.fields.get(name)
        label = field.label if field else 'Campo'
        kind = item['type']
        if kind == 'value_error' and 'ctx' in item:
            message = str(item['ctx']['error'])
            if name.startswith('email_'):
                message = 'Informe um e-mail válido.'
        elif kind in ('missing', 'string_too_short'):
            message = f'{label} é obrigatório.'
        elif kind == 'string_too_long':
            message = f'{label} deve ter até 100 caracteres.'
        elif field and field.kind == 'tel':
            message = 'Informe um telefone com DDD e 10 ou 11 dígitos.'
        elif field and field.kind in ('grade', 'hours'):
            message = f'{label} fora do intervalo permitido; use até duas casas decimais.'
        elif field and field.kind == 'date':
            message = f'{label} inválida.'
        else:
            message = f'{label} inválido. Confira o valor informado.'
        messages.append(message)
    return messages


def form_context(session, key, data=None):
    entity = ENTITIES[key]
    defaults = {}
    for name, field in entity.fields.items():
        if field.kind == 'date' and name != 'data_nascimento':
            defaults[name] = today().isoformat()
        elif field.kind == 'year':
            defaults[name] = today().year
        else:
            defaults[name] = ''
    relations = {field.relation: crud.options(session, field.relation)
                 for field in entity.fields.values() if field.kind == 'relation'}
    return {'entity': entity, 'data': defaults | (data or {}), 'relations': relations}


def show_form(request, session, key, action, record_id=None):
    data = {}
    if record_id is not None:
        data = crud.record_data(crud.get_record(session, ENTITIES[key], record_id), ENTITIES[key])
    return render(request, f'{key}.html', page=key, action=action, record_id=record_id,
                  **form_context(session, key, data))


def submit(request, session, key, action, form, record_id=None):
    entity = ENTITIES[key]
    record = None
    if record_id is not None:
        record = crud.get_record(session, entity, record_id)
    # Ignorar campos externos ao formulário impede alterações da chave primária.
    data = {name: form.get(name, '') for name in entity.fields}
    errors, status = [], 422
    if not valid_csrf(request, form.get('csrf')):
        errors = ['O formulário expirou. Recarregue a página e tente novamente.']
        status = 403
    elif action == 'delete':
        if form.get('confirm') != 'yes':
            errors = ['Confirme a exclusão para continuar.']
    else:
        try:
            values = entity.schema.model_validate(data).model_dump()
            errors = crud.validate_relations(session, entity, values)
        except ValidationError as error:
            errors = error_messages(error, entity)
    if not errors:
        try:
            if action == 'delete':
                session.delete(record)
            else:
                crud.save(session, entity, values, record)
            session.commit()
            request.session['flash'] = ['success', 'Registro excluído com sucesso.' if action == 'delete' else 'Dados salvos com carinho e sucesso!']
            return RedirectResponse(url(key), status_code=303)
        except DBAPIError as error:
            session.rollback()
            code = error.orig.args[0] if error.orig.args else None
            if code not in (1062, 1451, 1452, 3819, 1406, 1264):
                raise
            errors = [{
                1062: 'Já existe um registro com este e-mail ou uma matrícula deste aluno nesta turma.',
                1451: 'Este registro possui vínculos e não pode ser excluído. Consulte os detalhes e remova as dependências primeiro.',
                1452: 'Um dos registros vinculados não existe mais. Recarregue e escolha novamente.',
            }.get(code, 'Não foi possível salvar. Confira os campos e tente novamente.')]
            status = 409
    if action == 'delete':
        data = crud.record_data(record, entity)
    return render(request, f'{key}.html', page=key, action=action, record_id=record_id,
                  errors=errors, status=status, **form_context(session, key, data))


def make_router(key: str) -> APIRouter:
    entity = ENTITIES[key]
    router = APIRouter(prefix=f'/{key}', tags=[entity.title], default_response_class=HTMLResponse)
    # Documentar o corpo dos formulários, que continua sendo validado pelo schema.
    body_schema = entity.schema.model_json_schema()
    body_schema['properties']['csrf'] = {'type': 'string', 'description': 'Token do formulário GET da mesma sessão.'}
    body_schema['required'].append('csrf')
    form_docs = {'requestBody': {'required': True, 'content': {
        'application/x-www-form-urlencoded': {'schema': body_schema},
    }}}
    delete_docs = {'requestBody': {'required': True, 'content': {
        'application/x-www-form-urlencoded': {'schema': {
            'type': 'object', 'required': ['csrf', 'confirm'], 'properties': {
                'csrf': {'type': 'string'}, 'confirm': {'type': 'string', 'enum': ['yes']},
            },
        }},
    }}}

    @router.get('', name=f'{key}_list', summary=f'Listar {entity.title.lower()}')
    def list_records(request: Request, session: Database,
                     q: Annotated[str, Query(max_length=100)] = '',
                     especialidade: Annotated[str, Query(max_length=100)] = '',
                     p: Annotated[int, Query(ge=1)] = 1):
        context = crud.listing(session, key, q, especialidade, p)
        specialties = list(session.scalars(select(Professor.especialidade_professor).distinct().order_by(Professor.especialidade_professor))) if key == 'professores' else []
        return render(request, f'{key}.html', page=key, action='list', search=q,
                      specialty=especialidade, specialties=specialties, **context, **form_context(session, key))

    @router.get('/cadastrar', name=f'{key}_create_form', summary=f'Formulário de {entity.single}')
    def create_form(request: Request, session: Database):
        return show_form(request, session, key, 'create')

    @router.post('/cadastrar', name=f'{key}_create', summary=f'Cadastrar {entity.single}', openapi_extra=form_docs,
                 description='Envie os campos do formulário e o token csrf obtido no GET, com o cookie da mesma sessão.')
    async def create_record(request: Request, session: Database):
        form = await request.form(max_fields=30, max_files=0)
        return await run_in_threadpool(submit, request, session, key, 'create', form)

    @router.get('/{record_id}', name=f'{key}_view', summary=f'Detalhes de {entity.single}')
    def details(request: Request, session: Database, record_id: RecordId):
        record = crud.get_record(session, entity, record_id)
        return render(request, f'{key}.html', page=key, action='view', record_id=record_id,
                      **form_context(session, key, crud.record_data(record, entity)),
                      **crud.linked_records(session, key, record_id))

    @router.get('/{record_id}/editar', name=f'{key}_edit_form', summary=f'Formulário de edição de {entity.single}')
    def edit_form(request: Request, session: Database, record_id: RecordId):
        return show_form(request, session, key, 'edit', record_id)

    @router.post('/{record_id}/editar', name=f'{key}_edit', summary=f'Atualizar {entity.single}', openapi_extra=form_docs)
    async def edit_record(request: Request, session: Database, record_id: RecordId):
        form = await request.form(max_fields=30, max_files=0)
        return await run_in_threadpool(submit, request, session, key, 'edit', form, record_id)

    @router.get('/{record_id}/excluir', name=f'{key}_delete_form', summary=f'Confirmar exclusão de {entity.single}')
    def delete_form(request: Request, session: Database, record_id: RecordId):
        return show_form(request, session, key, 'delete', record_id)

    @router.post('/{record_id}/excluir', name=f'{key}_delete', summary=f'Excluir {entity.single}', openapi_extra=delete_docs,
                 description='Exige csrf válido e confirm=yes. Dependências impedem a exclusão.')
    async def delete_record(request: Request, session: Database, record_id: RecordId):
        form = await request.form(max_fields=30, max_files=0)
        return await run_in_threadpool(submit, request, session, key, 'delete', form, record_id)

    return router
