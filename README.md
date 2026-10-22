# Hello School 🎀 — Python + MySQL

Sistema escolar local do SENAI, migrado para **Python 3.11+, FastAPI, SQLAlchemy, PyMySQL e Jinja2**, com HTML, CSS e JavaScript puro. O tema e as funcionalidades foram preservados. Não há arquivos PHP nem dependência de Apache.

## Instalação e execução

Na pasta `schoolkitty`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `.env` com a **senha real da sua instalação MySQL**:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD="SUA_SENHA_LOCAL"
DB_NAME=escola_hello_kitty
SESSION_SECRET=
```

A senha ausente ou o texto de exemplo são rejeitados. Uma senha vazia só será utilizada se você a definir explicitamente, de acordo com seu servidor. Aspas preservam espaços e `#`. A conexão usa `URL.create`, permitindo caracteres especiais na senha sem concatená-la em uma URL.

Para manter a sessão após reinícios, gere uma chave com `python -c "import secrets; print(secrets.token_hex(32))"` e preencha `SESSION_SECRET`. Se ficar vazio, uma chave é gerada em memória a cada inicialização; formulários antigos precisarão ser recarregados.

Inicie seu MySQL Server e execute:

```powershell
uvicorn main:app --reload
```

- Site: **http://127.0.0.1:8000**
- Documentação local: **http://127.0.0.1:8000/docs**
- OpenAPI: **http://127.0.0.1:8000/openapi.json**

Se a política do PowerShell impedir a ativação, use diretamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Em Linux/macOS, ative com `source .venv/bin/activate` e copie com `cp .env.example .env`. A instalação inicial de pacotes requer internet; o funcionamento do sistema, incluindo imagens, fontes e documentação, é local.

## Aproveitar o banco existente

**Não reimporte o esquema ou o seed se você já possui o banco da versão anterior.** Configure `.env` para esse banco e inicie Uvicorn. Foram preservadas as tabelas `aluno`, `professor`, `curso`, `turma`, `matricula`, `nota` e a view `vw_alunos_cursos_turmas`.

A aplicação não chama `create_all`, não executa DDL, não importa o seed e não exclui tabelas na inicialização. O mapeamento SQLAlchemy usa as tabelas existentes.

Para uma **instalação nova**, use MySQL Server 8.0.16+:

1. Inicie MySQL pelo Laragon ou pelo aplicativo Serviços do Windows. Não precisa iniciar Apache. O MariaDB incluído em algumas versões do XAMPP não é o MySQL 8 solicitado.
2. Conecte pelo MySQL Workbench com host, porta, usuário e senha correspondentes ao `.env`.
3. Abra e execute `sql/database.sql` para criar o banco, tabelas, restrições e view.
4. Opcionalmente, execute `sql/seed.sql` **uma única vez em tabelas vazias**. Em caso de erro na transação, execute `ROLLBACK;` e corrija a causa antes de repetir.
5. No dashboard, o seed resulta em **10 alunos, 5 professores, 5 cursos, 5 turmas, 10 matrículas e média 8,43**.

Utilize o Workbench para inspecionar os dados. Após alterar registros, recarregue o site. Nenhum indicador é fixado no frontend.

## Funcionalidades e rotas

| Área | Rota | Recursos |
| --- | --- | --- |
| Dashboard | `/` | Contagens reais, média geral e matrículas recentes |
| Alunos | `/alunos` | CRUD, busca por nome e histórico de matrículas |
| Professores | `/professores` | CRUD, busca, filtro de especialidade e turmas vinculadas |
| Cursos | `/cursos` | CRUD, carga horária e turmas associadas |
| Turmas | `/turmas` | CRUD, busca por curso, vínculos e matrículas |
| Matrículas | `/matriculas` | CRUD, situação, busca por aluno e notas com média |
| Notas | `/notas` | CRUD, busca por aluno e identificação de aluno/curso/turma |
| Relatórios | `/relatorios` | Nove consultas SQL e filtros dinâmicos |

Cada módulo tem `GET /modulo`, `GET/POST /modulo/cadastrar`, `GET /modulo/{id}`, `GET/POST /modulo/{id}/editar` e `GET/POST /modulo/{id}/excluir`. O GET de exclusão **somente mostra a confirmação**. Listagens têm 15 registros por página.

Relatórios: alunos; professores e turmas; cursos; alunos por turma; notas por aluno; médias por matrícula; quantidade de alunos por turma; matrículas por situação; consulta da view.

As rotas retornam HTML e recebem formulários, não constituem um CRUD JSON separado. POST usa `application/x-www-form-urlencoded`, os campos da tela, o token `csrf` e o cookie da mesma sessão. Exclusão exige `confirm=yes`. Sucesso redireciona com 303; validação retorna 422, CSRF inválido 403 e conflito de integridade 409. A documentação de rotas em `/docs` funciona sem CDN.

## Organização

```text
main.py                  Aplicação, dashboard, arquivos estáticos e erros
 database.py             .env, engine SQLAlchemy e sessão por requisição
 models.py               Seis entidades e relacionamentos ORM
 schemas.py              Validações Pydantic
 crud.py                 Persistência, consultas, históricos e indicadores
 entities.py             Metadados dos campos
 queries.py              SQL dos relatórios e seleções relacionais
 security.py             Proteção CSRF
 views.py                Contexto, URLs e formatação Jinja2
 requirements.txt        Dependências de execução
 requirements-dev.txt    Dependências opcionais de teste
 .env.example            Modelo de configuração sem segredos
 routers/
   common.py             Controlador compartilhado dos CRUDs
   alunos.py / professores.py / cursos.py / turmas.py
   matriculas.py / notas.py / relatorios.py
 templates/
   base.html / index.html / dashboard.html / crud.html
   alunos.html / professores.html / cursos.html / turmas.html
   matriculas.html / notas.html / relatorios.html
   docs.html / error.html / partials/
 static/css/style.css
 static/js/script.js
 static/img/             Ilustrações SVG locais
 sql/
   database.sql / seed.sql / consultas.sql
 tests/
   test_schemas.py        Validação sem banco
   test_mysql.py          ORM, integridade, rotas, relatórios e estados vazios
   test_http.py           Cadeia completa de formulários por HTTP
   browser_check.py       Navegação e responsividade no Chrome
 TESTES.md                Resultados efetivamente verificados
```

## Migração e regras preservadas

A conexão anterior foi substituída por `database.py`; validações e segurança por `schemas.py`, `security.py` e middleware; controlador e cadastros por `routers/common.py`, `crud.py` e templates. Dashboard, históricos e relatórios utilizam consultas reais com SQLAlchemy/SQL parametrizado. Cabeçalho, sidebar, rodapé e formulários agora são Jinja2. Cada módulo possui seu template, que herda o CRUD compartilhado para evitar duplicação.

O código original e as configurações `.htaccess` foram removidos **depois** de validar os fluxos equivalentes. A pasta atual pode ser servida diretamente por Uvicorn, sem copiar para `htdocs` ou `www`.

- E-mails são únicos dentro de alunos e professores. Matrícula é única por aluno/turma, independentemente da situação.
- FKs usam RESTRICT. O ORM não apaga dependências automaticamente; remova notas, matrículas e turmas explicitamente quando necessário.
- Notas usam DECIMAL(4,2), entre 0 e 10; carga horária positiva; ano 1900–2100; semestre 1 ou 2; turno/situação em listas permitidas.
- Pydantic valida e-mail, telefone, datas, nascimento sem data futura, tamanhos, limites e precisão. As referências são consultadas antes de gravar; as FKs também protegem contra mudanças concorrentes.
- Média por matrícula é aritmética e informativa. Média geral considera todas as avaliações. A contagem por turma inclui todas as situações.
- A identificação da turma combina ID, ano, semestre e turno; não foi adicionada coluna `nome_turma`.
- Alterar situação preserva a matrícula, sem criar uma tabela de versões anteriores das situações.

## Segurança e transações

Consultas ORM e SQL usam parâmetros vinculados. Nomes de entidades/colunas vêm de metadados internos. Jinja2 escapa a saída HTML. Os formulários têm CSRF vinculado à sessão assinada; o cookie utiliza HttpOnly e SameSite=Lax. O middleware envia CSP e bloqueia enquadramento por outros sites.

Cada requisição tem uma sessão SQLAlchemy. Gravações usam `commit`; conflitos executam `rollback`. O fechamento desfaz transações pendentes, evitando alterações parciais.

Credenciais ficam em `.env`, ignorado pelo Git. Somente `/static` é exposto como diretório público: código, `.env`, SQL, testes e templates não são servidos. Não coloque segredos em `/static`. Falhas de banco retornam orientação segura com 503, sem senha ou SQL interno.

O sistema não possui autenticação e destina-se exclusivamente ao uso local. Mantenha o endereço padrão `127.0.0.1`; não exponha publicamente sem autenticação, autorização e controles adicionais. A identidade temática é educacional, sem afiliação oficial à Sanrio.

## Testes

```powershell
pip install -r requirements-dev.txt
python -m pytest tests/test_schemas.py -q
```

Para integração, prepare **um banco descartável com nome terminado em `_test`**. Importe cópias dos scripts SQL substituindo o banco por `escola_hello_kitty_test`; nunca faça isso no banco de uso. Configure:

```powershell
$env:DB_NAME = 'escola_hello_kitty_test'
$env:RUN_MYSQL_TESTS = '1'
python -m pytest tests/test_mysql.py -q
```

Host, porta, usuário e senha podem vir do `.env` ou do ambiente. Variáveis do processo têm precedência. Os testes MySQL usam uma transação externa com rollback; AUTO_INCREMENT pode avançar. Sem `RUN_MYSQL_TESTS=1`, são marcados como não executados.

Com Uvicorn também apontando para o banco descartável:

```powershell
python tests/test_http.py http://127.0.0.1:8000
python tests/browser_check.py http://127.0.0.1:8000
```

O teste de navegador requer Chrome instalado, espera os indicadores originais do seed e verifica 1440px/768px/390px. Capturas ficam em `.tools/screenshots`. Testes HTTP/navegador criam e excluem registros; se interrompidos, podem sobrar registros com prefixos `HTTP` ou `Navegador`. Use somente banco descartável. Consulte `TESTES.md` para resultados e limitações.

## Problemas comuns

- **Vamos conectar sua escola?** Confira serviço MySQL, host, porta, senha, banco e `.env`. Se já possui o banco, não o recrie.
- **Acesso negado**: teste as credenciais no Workbench. Não presuma senha root vazia.
- **Tabela/view ausente**: confira os objetos no Workbench. Importe o DDL para instalação nova ou restaure manualmente o objeto ausente após avaliar seus dados.
- **Porta 3306 ocupada**: escolha o serviço correto ou ajuste `DB_PORT` também no Workbench.
- **Porta 8000 ocupada**: use `uvicorn main:app --reload --port 8001`.
- **Uvicorn não encontrado**: ative `.venv` ou use o Python do ambiente com `-m uvicorn`.
- **Formulário expirado**: recarregue a página. Pode acontecer após reiniciar sem `SESSION_SECRET` fixo.
- **Falha ao instalar pacotes**: confirme Python 3.11+ e o ambiente virtual ativo.
- **Duplicidade no seed**: não reaplique no banco de uso.

`sql/consultas.sql` mantém os exemplos didáticos de DDL, DML, DQL e DCL. Comandos mutáveis e de permissão estão comentados e não são executados pelo site.
