# Escola Kawaii — projeto acadêmico de gestão escolar

Portfólio público e protótipo de painel para apresentar uma proposta de centralização dos dados escolares em um banco relacional.

## O que existe

- Portfólio público em `index.html`, com problema, proposta, funcionalidades previstas e diagrama didático das seis entidades.
- Login do administrador em `login.html` e sessão assinada no servidor. Não há cadastro público nem senha padrão.
- Arquivo `/painel.html` protegido por middleware da Vercel, com logout e consultas somente de leitura.
- Funções de servidor Node.js para autenticação e consulta MySQL parametrizada/limitada. Os nomes e colunas refletem o esquema didático que já estava documentado; o esquema físico original não foi entregue.
- Os indicadores são contados no banco conectado; sem conexão, o painel informa a indisponibilidade e não inventa valores.

O repositório não contém SQL ou DER original, banco conectado, dados reais ou nomes dos integrantes. A VIEW `vw_alunos_cursos_turmas` é esperada conforme a documentação educativa existente, mas sua existência e colunas precisam ser confirmadas no banco antes de publicar com dados. A consulta da view assume `nome_aluno`, `nome_curso` e `identificacao_turma`.

## Preparar o ambiente

Requisitos: Node.js 20 ou superior, conta/projeto Vercel para servir funções e middleware, e banco MySQL 8.0 acessível ao servidor.

1. Execute `npm install`. Para desenvolvimento local, o servidor incluído é iniciado com `npm run dev`; ele lê as variáveis de `.env.local`. Para publicação, conecte o repositório ao projeto Vercel pelo painel e configure as variáveis privadas antes do deploy.
2. Gere um hash local em um terminal interativo com `npm run make-password-hash`; digite uma senha administrativa com ao menos 12 caracteres quando solicitado. Configure o hash exibido em `ADMIN_PASSWORD_HASH`; configure também `ADMIN_USERNAME` e `SESSION_SECRET` com um segredo aleatório forte (pelo menos 32 bytes).
3. Configure `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` e `DB_SSL=true` no ambiente local (`.env.local`, não versionado) e nas variáveis privadas do projeto Vercel. O usuário MySQL deve ter somente permissões de leitura necessárias. Não coloque credenciais nos arquivos versionados nem no código do navegador.
4. Confirme as seis tabelas, nomes de colunas, chaves, relacionamentos e a view no banco existente. Esta implementação não cria nem migra tabelas. Se a view ou algum campo divergir, ajuste a consulta depois de comparar com o modelo aprovado.
5. Para desenvolvimento local, rode `npm run dev` e abra `http://127.0.0.1:3000`. Abrir `index.html` direto como arquivo não executa as funções de servidor.
6. Para publicar, configure as variáveis no painel do projeto Vercel e faça deploy pelo painel ou integração Git. Use HTTPS e permita conexões MySQL somente a partir da infraestrutura necessária.

Não reutilize senhas de exemplo no terminal ou em histórico compartilhado. `.env.example` lista os nomes esperados, sem valores secretos.

## Verificação

`npm run dev` inicia o servidor local incluído e lê as variáveis de `.env.local`. Teste portfólio, login, acesso direto a `/painel.html`, credenciais erradas, logout, seção de cada tabela, resumo e VIEW depois de configurar uma conta e um banco de teste. A partir desta cópia não é possível validar credenciais válidas nem consultas reais: não foram fornecidos usuário/hash administrativo, banco, esquema físico ou dados. Sem essas variáveis, as funções respondem com estado de configuração ausente, sem liberar o painel.

A aplicação implementa leitura e não CRUD. Edição/exclusão/cadastro requerem validação das regras escolares e do esquema real. Nenhuma alteração física do banco é executada.

## Modelo didático preexistente

`ALUNO`, `PROFESSOR`, `CURSO`, `TURMA`, `MATRICULA` e `NOTA`; TURMA referencia CURSO e PROFESSOR, MATRICULA referencia ALUNO e TURMA e NOTA referencia MATRICULA. Os exemplos SQL da página são material educativo e não foram executados.




