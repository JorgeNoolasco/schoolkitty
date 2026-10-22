# Escola Kawaii — Banco de Dados SENAI CTTI

Site acadêmico responsivo sobre banco de dados, modelagem relacional e SQL. O repositório original estava vazio, sem backend, banco ou esquema SQL; este projeto apresenta o modelo proposto e mantém explícito o que ainda precisa ser conectado.

## Rodar localmente

Abra `index.html` em um servidor estático. Configure em `config.js` a URL da API, se houver. A URL padrão é `/api`. A seção Gerenciamento consulta `GET /alunos`, `GET /professores`, `GET /cursos`, `GET /turmas`, `GET /matriculas` e `GET /notas`; os contratos são propostas e não foram verificados contra um servidor.

Não há operações de escrita no cliente. Para implementar CRUD, o backend deve definir autenticação, autorização, validações e regras de integridade antes de habilitar qualquer escrita.

## Deploy estático na Vercel

Importe o repositório como site estático, com raiz do projeto como diretório e sem build command. `vercel.json` configura somente a entrega estática. Não cria funções Python nem backend. Para front e API separados, use URL HTTPS em `config.js` e CORS restrito à origem publicada. Não use localhost em produção.

## Conteúdo implementado

- Fundamentos: banco, dado/informação, SGBD, vantagens, entidades, atributos e relacionamentos.
- Modelos hierárquico e relacional com comparação.
- Modelagem conceitual, lógica e física das entidades ALUNO, PROFESSOR, CURSO, TURMA, MATRICULA e NOTA.
- Exemplos DDL, DML, DQL, DCL, cinco desafios e VIEW `vw_alunos_cursos_turmas`; comandos apenas copiáveis, não executáveis pelo navegador.
- Comparação educativa de PostgreSQL, IBM Db2, Firebird, Oracle Database e Microsoft SQL Server, com fontes oficiais na página.
- Mascote SVG vetorial original, layout responsivo, menu mobile, abas, estados de API e preferência por movimento reduzido.

## Modelo e cautelas

Os tipos físicos exibidos são uma proposta didática MySQL. O esquema real não foi fornecido. A view pode já existir e deve ser preservada após inspeção. `DECIMAL(2,2)` não comporta nota 10,00; considere `DECIMAL(4,2)` para escala de 0 a 10, mas confirme o tipo real, dependências e autorização antes de preparar/aplicar migração. A restrição UNIQUE de matrícula por aluno/turma também precisa de confirmação pelas regras acadêmicas reais.

Exemplos de INSERT com nomes `Exemplo A/B/C` e e-mails `@exemplo.edu` são somente SQL ilustrativo; não são dados persistidos. `GRANT` é explicativo, sua sintaxe varia por SGBD e deve ser executada apenas por administrador com privilégio mínimo.

## Pendências

- Backend FastAPI, conexão remota MySQL e variáveis privadas de ambiente.
- Confirmar banco `escola_hello_kitty`, entidades, tipos, chaves, regras, view e endpoints reais.
- Autenticação, autorização e operações CRUD protegidas no servidor.
- Migração aprovada para tipo de nota, se necessária.
- PDF e apresentação PowerPoint/Canva são entregas separadas; este site é complementar.

## Fontes de comparação

Links oficiais usados estão nas fichas de cada produto. Licenciamento, limites e recursos variam por edição/versão. A comparação não afirma benchmarks nem preços específicos.
