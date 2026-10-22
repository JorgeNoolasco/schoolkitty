"""Contexto e formatação para templates Jinja2 com escape automático."""
from datetime import date
from decimal import Decimal
from urllib.parse import urlencode

from fastapi.templating import Jinja2Templates

from database import BASE_DIR
from entities import ENTITIES
from schemas import today
from security import csrf_token

templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))


def url(page='dashboard', action=None, id=None, **params):
    path = '/' if page == 'dashboard' else f'/{page}'
    if action == 'create':
        path += '/cadastrar'
    elif action in ('view', 'edit', 'delete'):
        path += f'/{id}'
        path += {'view': '', 'edit': '/editar', 'delete': '/excluir'}[action]
    return path + ('?' + urlencode(params) if params else '')


def number(value):
    return '—' if value is None else f'{value:.2f}'.replace('.', ',')


def display(value, field=None, relations=None):
    if field and field.kind == 'relation':
        return (relations or {}).get(field.relation, {}).get(str(value), 'Registro indisponível')
    if value is None:
        return '—'
    if isinstance(value, date):
        return value.strftime('%d/%m/%Y')
    if isinstance(value, Decimal) or (field and field.kind in ('grade', 'hours')):
        return number(Decimal(value))
    return str(value)


def form_value(value):
    return value.isoformat() if isinstance(value, date) else str(value)


templates.env.globals.update(url=url, display=display, number=number, str=str, form_value=form_value)


def render(request, template, *, page='dashboard', title=None, status=200, **context):
    common = {
        'request': request, 'page': page, 'title': title or (ENTITIES[page].title if page in ENTITIES else 'Visão geral'),
        'entities': ENTITIES, 'today': today(), 'csrf': csrf_token(request),
        'flash': request.session.pop('flash', None), 'errors': [],
    }
    return templates.TemplateResponse(request=request, name=template, context=common | context, status_code=status)
