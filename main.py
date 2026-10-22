"""Aplicação local: uvicorn main:app --reload."""
import os
import secrets

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware

import crud
from database import BASE_DIR, DatabaseConfigurationError
from routers import alunos, cursos, matriculas, notas, professores, relatorios, turmas
from routers.common import Database
from views import render

app = FastAPI(title='Hello School', version='2.0.0',
              description='Gestão escolar local com formulários HTML e proteção CSRF.', docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SESSION_SECRET') or secrets.token_hex(32),
                   session_cookie='schoolkitty_session', same_site='lax', max_age=7200)
app.mount('/static', StaticFiles(directory=BASE_DIR / 'static'), name='static')


@app.middleware('http')
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'same-origin'
    if not request.url.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.exception_handler(DatabaseConfigurationError)
@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, error):
    return render(request, 'error.html', title='Conexão com a escola', status=503, connection_error=True)


@app.exception_handler(HTTPException)
async def http_error(request: Request, error):
    message = 'Registro ou página não encontrado.' if error.status_code == 404 else 'Não foi possível atender esta solicitação.'
    return render(request, 'error.html', title='Vamos conferir?', status=error.status_code, message=message)


@app.exception_handler(RequestValidationError)
async def request_error(request: Request, error):
    return render(request, 'error.html', title='Confira a solicitação', status=422,
                  message='Parâmetros inválidos. Confira os filtros e a identificação do registro.')


@app.get('/', response_class=HTMLResponse, tags=['Dashboard'], summary='Indicadores e matrículas recentes')
def dashboard(request: Request, session: Database):
    return render(request, 'index.html', **crud.dashboard(session))


for module in (alunos, professores, cursos, turmas, matriculas, notas, relatorios):
    app.include_router(module.router)


@app.get('/docs', response_class=HTMLResponse, include_in_schema=False)
def documentation(request: Request):
    # Documentação local: não depende de JavaScript ou fontes de uma CDN.
    return render(request, 'docs.html', title='Documentação das rotas', paths=app.openapi()['paths'])
