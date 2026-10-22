# SchoolKitty

Frontend estático inicial para uma plataforma escolar, feito com HTML, CSS e JavaScript nativos. O repositório entregue estava vazio (sem código de aplicação, esquema SQL ou API); esta base mantém essa distinção explícita. O painel consulta a API por HTTP e informa quando ela não está disponível. Não há dados simulados nem persistência local.

## Executar localmente

Abra `index.html` em um servidor estático local. A configuração padrão aponta para `/api`; sem backend, os blocos mostram uma mensagem de indisponibilidade. Para usar um backend separado, edite `config.js`:

```js
window.APP_CONFIG = {
  API_BASE_URL: "https://seu-backend.vercel.app/api",
  REQUEST_TIMEOUT_MS: 10000
};
```

Não use `localhost` como URL publicada. Não coloque credenciais ou connection strings neste repositório. A autenticação do cliente usa `credentials: "include"` como preparação para cookies de sessão HttpOnly; o servidor também precisa configurar `Secure`, `SameSite`, CSRF e CORS para as origens exatas.

## Deploy frontend na Vercel

Importe o repositório como projeto estático, mantenha a raiz do projeto como diretório raiz e deixe o build command vazio. Configure `API_BASE_URL` no `config.js` com a URL HTTPS real do backend antes do deploy. O `vercel.json` só configura a entrega estática: ele não cria funções Python nem uma API.

## Estrutura

- `index.html`: painel responsivo.
- `styles.css`: identidade visual, navegação móvel e componentes.
- `config.js`: URL e timeout configuráveis.
- `api.js`: Fetch, timeout, cookies e tratamento de respostas HTTP.
- `app.js`: navegação e carregamento dos blocos do painel.
- `vercel.json`: configuração da entrega estática.

## Contrato de API esperado pelo painel

Os caminhos abaixo são contratos propostos pelo frontend, não rotas verificadas ou implementadas. As respostas podem ser arrays ou objetos com `items`/`data`.

| Método | Rota | Uso/campos esperados |
|---|---|---|
| GET | `/api/turmas` | Lista; `nome_curso`, `nome_turma`, `nome_professor`, `quantidade_alunos` |
| GET | `/api/atividades?limit=4` | Lista; `titulo`, `nome_turma`, `prazo`, `status` |
| GET | `/api/calendario?limit=3` | Lista; `dia`, `mes`, `titulo`, `nome_curso` |
| GET | `/api/alunos?limit=1` | Lista ou resumo com total |
| POST | `/api/auth/logout` | Encerra sessão autenticada |

Use códigos HTTP convencionais (`401`, `403`, `404`, `422`, `429`, `500`) e mensagens públicas seguras. Cadastros e operações de gestão ainda não são enviados pelo painel; precisam dos endpoints reais, autenticação, validação e autorização no backend.

## Backend, banco e pendências

Não há backend FastAPI nem conexão MySQL neste checkout. Antes de implementar persistência, confirmar o esquema real, preservar `escola_hello_kitty` e a view `vw_alunos_cursos_turmas`, e conferir tipos e vínculos. `DECIMAL(2,2)` não comporta a faixa 0–10; propor `DECIMAL(4,2)` ou escala definida pelo projeto ao responsável pelo banco antes de alterar qualquer tabela.

O modelo informado não inclui usuários/credenciais, atividades, entregas, eventos nem avisos. Login, papéis, autorização, notas e esses módulos dependem de API e esquema aprovados. Para atividades/entregas será preciso definir tabelas, vínculos, prazos, submissões e feedback. A demonstração da view deve ser feita por endpoint de leitura autenticado. Exemplos DDL, DML, DQL e DCL e scripts SQL também dependem de receber o esquema real; comandos DCL devem ficar em scripts separados, nunca em um editor SQL irrestrito.

## Segurança

O navegador nunca conecta ao MySQL. O backend deve validar entrada, identidade, papel e vínculo do usuário com cada recurso, limitar CORS, proteger sessões contra CSRF e não retornar erros internos. O frontend escapa texto ao renderizar conteúdo externo e aplica timeout nas solicitações. Configure HTTPS em produção.
