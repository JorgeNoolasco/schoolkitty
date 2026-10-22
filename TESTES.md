# Migração Python — verificação em 22/10/2026

Ambiente: Windows, Python 3.13, FastAPI 0.159.1, SQLAlchemy 2.0.55, PyMySQL 1.2.3, Pydantic 2.14.1, Uvicorn 0.54.0 e MySQL Community Server 8.4.3. Chrome via Playwright.

O MySQL de teste utilizou instância isolada na porta 3307, diretório próprio e senha aleatória. Os scripts existentes foram importados em `escola_hello_kitty_test`, alterando somente o nome do banco na cópia enviada ao cliente. Nenhum banco de uso foi recriado ou alterado pela migração.

## Resultados executados

| Verificação | Resultado |
| --- | --- |
| Validações Pydantic: telefone, e-mail, datas, limites e precisão | 18 testes passaram |
| Integração ORM/MySQL, rotas, relatórios, CSRF e estados vazios | 4 testes passaram |
| Cadeia HTTP de cadastro, detalhes, edição e exclusão dos seis módulos | Passou |
| Relações aluno/professor/curso/turma/matrícula/nota | Preservadas |
| E-mails duplicados e matrícula duplicada | Bloqueados |
| FK inexistente e exclusões com dependências | Bloqueadas |
| CHECKs MySQL de carga horária e intervalo de notas | Aplicados |
| Notas 0,00, 8,50 e 10,00 e média por matrícula | Passou |
| View com registros reais, incluindo registro recém-criado | Passou |
| Nove relatórios, busca, filtro de especialidade e seleções relacionais | Passaram |
| Entrada semelhante a SQL na busca e script no nome | Tratados como texto/HTML escapado |
| POST sem CSRF e exclusão sem confirmação | Bloqueados |
| Dashboard: 10/5/5/5/10 e média 8,43 com seed | Conferido no navegador |
| Layout em 1440px, 768px e 390px | Sem transbordamento da página |
| Cadastro, edição e exclusão pelo formulário no Chrome | Passou |
| Menu mobile e seleção automática de relatório | Passou |
| JavaScript das telas verificadas | Sem exceções |
| .env, código, templates, SQL, README e .git via HTTP | Retornaram 404 |
| /docs e /openapi.json | Disponíveis sem CDN |
| Inicialização sem credenciais | Site retorna orientação segura com 503; /docs disponível |

Os testes pytest totalizaram **22 aprovações**. Houve um aviso de depreciação do adaptador `httpx` do TestClient instalado; não impediu os testes nem afeta Uvicorn. HTTP e Chrome foram testados adicionalmente contra o servidor real.

O código original foi mantido durante a conversão e removido depois de validar os fluxos equivalentes. Os testes não dependem de PHP ou Apache. O esquema SQL foi preservado e não é executado na inicialização da aplicação.

## Verificações restantes na instalação do usuário

- Configurar senha, porta e banco no `.env` e iniciar Uvicorn no ambiente permanente.
- Inspecionar o banco existente pela interface do Workbench; a importação de teste utilizou o cliente MySQL.
- Executar especificamente em Python 3.11/3.12: o ambiente disponível usou 3.13, embora o requisito mínimo seja 3.11.
- Outros navegadores, dispositivos físicos, leitor de tela e uso simultâneo por vários usuários.

Os procedimentos para repetir os testes estão no README. Todos os testes que alteram dados devem usar um banco descartável.
