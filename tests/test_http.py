"""Testes HTTP para uma instalação local descartável, sem dependências externas."""
import html
import http.cookiejar
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

def run(base_url):
    base = base_url.rstrip('/') + '/'
    client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


    def request(page='dashboard', action=None, record=None, data=None, **params):
        path = '' if page == 'dashboard' else page
        if action == 'create':
            path += '/cadastrar'
        elif action in ('view', 'edit', 'delete'):
            path += '/' + str(record) + {'view':'', 'edit':'/editar', 'delete':'/excluir'}[action]
        url = base + path + ('?' + urllib.parse.urlencode(params) if params else '')
        payload = urllib.parse.urlencode(data).encode() if data is not None else None
        try:
            response = client.open(url, payload)
        except urllib.error.HTTPError as error:
            response = error
        return response.status, response.read().decode('utf-8')


    def check(condition, message):
        if not condition:
            raise AssertionError(message)
        print('OK:', message)


    def token(body):
        return re.search(r'name="csrf" value="([^"]+)"', body)[1]


    def post(page, action, data, record=None):
        status, body = request(page, action, record)
        check(status == 200, f'Formulário {page}/{action}')
        return request(page, action, record, data={'csrf': token(body), **data})


    suffix = str(time.time_ns())
    name = 'HTTP ' + suffix
    records = []
    try:
        status, dashboard = request()
        check(status == 200 and 'Matrículas recentes' in dashboard and 'Vamos conectar' not in dashboard, 'Dashboard conectado')
        for page in ['alunos', 'professores', 'cursos', 'turmas', 'matriculas', 'notas']:
            check(request(page)[0] == 200, 'Listagem ' + page)
        for report in ['alunos', 'professores', 'cursos', 'turma', 'notas', 'medias', 'quantidade', 'situacao', 'view']:
            check(request('relatorios', report=report)[0] == 200, 'Relatório ' + report)

        def create(page, values):
            status, body = post(page, 'create', values)
            check(status == 200 and 'Dados salvos' in body, 'Cadastro HTTP ' + page)
            record = int(re.search(r'href="/' + page + r'/(\d+)"', body)[1])
            records.append((page, record))
            check(request(page, 'view', record)[0] == 200, 'Detalhes ' + page)
            check('Dados salvos' in post(page, 'edit', values, record)[1], 'Edição HTTP ' + page)
            return record

        aluno_data = dict(nome_aluno=name, data_nascimento='2007-01-01', email_aluno=suffix+'@example.com', telefone_aluno='11900000999')
        aluno = create('alunos', aluno_data)
        check('Já existe' in post('alunos', 'create', aluno_data)[1], 'E-mail duplicado na interface')
        check('futuro' in post('alunos', 'create', {**aluno_data, 'data_nascimento':'2999-01-01'})[1], 'Nascimento futuro bloqueado')
        check(request('alunos', 'create', data={**aluno_data, 'csrf':'invalido'})[0] == 403, 'CSRF inválido bloqueado')
        check(name in request('alunos', q=name)[1], 'Busca por nome')
        check('Nenhum registro' in request('alunos', q="' OR 1=1 --")[1], 'Busca trata SQL como texto')
        xss = '<script>alert(1)</script>'
        post('alunos', 'edit', {**aluno_data, 'nome_aluno': xss}, aluno)
        body = request('alunos', 'view', aluno)[1]
        check(html.escape(xss) in body and xss not in body, 'Saída HTML escapa XSS')
        post('alunos', 'edit', aluno_data, aluno)
        professor = create('professores', dict(nome_professor=name, email_professor=suffix+'@example.com', telefone_professor='11900000998', especialidade_professor=name))
        check(name in request('professores', especialidade=name)[1], 'Filtro de especialidade')
        curso = create('cursos', dict(nome_curso=name, descricao_curso='Teste HTTP', cargahoraria_curso='80'))
        turma_data = dict(id_curso=curso, id_professor=professor, ano_letivo='2026', semestre_turma='2', turno_turma='manhã')
        turma = create('turmas', turma_data)
        check('não existe' in post('turmas', 'create', {**turma_data, 'id_curso':'999999999'})[1], 'Vínculo inexistente bloqueado')
        matricula_data = dict(id_aluno=aluno, id_turma=turma, data_matricula='2026-10-22', situacao_matricula='ativa')
        matricula = create('matriculas', matricula_data)
        check('Já existe' in post('matriculas', 'create', matricula_data)[1], 'Matrícula duplicada bloqueada')
        nota_data = dict(id_matricula=matricula, descricao_nota='Avaliação HTTP', valor_nota='8.50', data_nota='2026-10-22')
        nota = create('notas', nota_data)
        check('fora do intervalo' in post('notas', 'create', {**nota_data, 'valor_nota':'10.01'})[1], 'Nota inválida bloqueada no backend')
        check('Média: 8,50' in request('matriculas', 'view', matricula)[1], 'Média no detalhe da matrícula')
        check(name in request('relatorios', report='view')[1], 'Registro novo aparece na VIEW')
        check('vínculos' in post('alunos', 'delete', {'confirm':'yes'}, aluno)[1], 'Exclusão com dependências bloqueada')
        check('Confirme a exclusão' in post('notas', 'delete', {}, nota)[1], 'Exclusão exige confirmação')
        check(request('notas', 'view', nota)[0] == 200, 'GET de confirmação preserva o registro')
    finally:
        for page, record in reversed(records):
            status, body = post(page, 'delete', {'confirm':'yes'}, record)
            check(status == 200 and 'Registro excluído' in body, 'Exclusão HTTP ' + page)

    check(request('inexistente')[0] == 404, 'Rota desconhecida retorna 404')
    print('Testes HTTP concluídos.')


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8000')
