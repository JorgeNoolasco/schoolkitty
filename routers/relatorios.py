"""Relatórios SQL parametrizados, incluindo a view já existente."""
from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

import crud
from queries import REPORTS
from views import render
from .common import Database

router = APIRouter(tags=['Relatórios'])


@router.get('/relatorios', response_class=HTMLResponse, summary='Consultar relatórios e a view')
def reports(request: Request, session: Database,
            report: Annotated[str, Query(max_length=30)] = 'view',
            filter: Annotated[str, Query(max_length=100)] = ''):
    key = report if report in REPORTS else 'view'
    selected = REPORTS[key]
    kind = selected['filter_kind']
    options = {}
    if kind:
        options = {value: value for value in ('ativa', 'concluída', 'cancelada', 'trancada')} if kind == 'situacao' else crud.options(session, kind)
        if filter not in options:
            filter = next(iter(options), '')
    linked = [] if kind and not filter else crud.rows(session, selected['sql'], {'filter_value': filter} if kind else {})
    return render(request, 'relatorios.html', page='relatorios', title='Consultas e Relatórios',
                  reports=REPORTS, report_key=key, report=selected, options=options, filter=filter, linked=linked)
