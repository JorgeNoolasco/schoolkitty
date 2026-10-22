(() => {
    const $ = (q, r = document) => r.querySelector(q), toast = (text) => { const n = document.createElement("div"); n.className = "toast"; n.textContent = text; $("#toastRegion").append(n); setTimeout(() => n.remove(), 3500) };
    $("#menuButton").addEventListener("click", () => { const opened = $("#mainNav").classList.toggle("open"); $("#menuButton").setAttribute("aria-expanded", String(opened)) });
    $("#mainNav").addEventListener("click", e => { if (e.target.closest("a")) { $("#mainNav").classList.remove("open"); $("#menuButton").setAttribute("aria-expanded", "false") } });
    document.querySelectorAll("[data-tab]").forEach(button => button.addEventListener("click", () => {
        document.querySelectorAll("[data-tab]").forEach(tab => { const selected = tab === button; tab.classList.toggle("active", selected); tab.setAttribute("aria-selected", String(selected)) });
        document.querySelectorAll(".tab-panel").forEach(panel => { const selected = panel.id === "panel-" + button.dataset.tab; panel.hidden = !selected; panel.classList.toggle("active", selected) });
    }));
    const examples = {
        ddl: { stamp: "CREATE", title: "DDL · Data Definition Language", desc: "Define estruturas, tabelas e restrições.", label: "DESAFIO 01 · CRIAR TABELA", note: "Confira o esquema existente antes de criar ou alterar tabelas.", code: "CREATE TABLE aluno (\\n  id_aluno INT PRIMARY KEY AUTO_INCREMENT,\\n  nome_aluno VARCHAR(120) NOT NULL,\\n  data_nascimento DATE,\\n  email_aluno VARCHAR(254) UNIQUE,\\n  telefone_aluno VARCHAR(24)\\n);" },
        dml: { stamp: "INSERT", title: "DML · Data Manipulation Language", desc: "Insere, atualiza e remove registros. Use filtros e revisão antes de alterar.", label: "DESAFIOS 02 E 03 · INSERT + UPDATE", note: "Os nomes e e-mails são exemplos de comandos, não registros armazenados.", code: "INSERT INTO aluno (nome_aluno, email_aluno)\\nVALUES ('Exemplo A', 'a@exemplo.edu'),\\n       ('Exemplo B', 'b@exemplo.edu'),\\n       ('Exemplo C', 'c@exemplo.edu');\\n\\nUPDATE aluno SET email_aluno = 'novo@exemplo.edu'\\nWHERE id_aluno = 1;\\n\\n-- DELETE exige autorização e filtro conferido\\nDELETE FROM aluno WHERE id_aluno = 1;" },
        dql: { stamp: "SELECT", title: "DQL · Data Query Language", desc: "Consulta registros e combina relações com condições.", label: "DESAFIO 04 · SELECT + WHERE + JOIN", note: "Exemplo didático. Execute apenas em ambiente de estudo preparado.", code: "SELECT a.nome_aluno, c.nome_curso, t.ano_letivo\\nFROM aluno AS a\\nJOIN matricula AS m ON m.id_aluno = a.id_aluno\\nJOIN turma AS t ON t.id_turma = m.id_turma\\nJOIN curso AS c ON c.id_curso = t.id_curso\\nWHERE a.id_aluno = 1;" },
        dcl: { stamp: "GRANT", title: "DCL · Data Control Language", desc: "Controla privilégios; deve ser aplicado por pessoa administradora.", label: "DESAFIO 05 · CONCEDER LEITURA", note: "Sintaxe MySQL ilustrativa. Nunca conceda privilégios administrativos a visitantes.", code: "GRANT SELECT ON escola.aluno\\nTO 'leitor'@'%';" }
    };
    document.querySelectorAll("[data-sql]").forEach(button => button.addEventListener("click", () => {
        document.querySelectorAll("[data-sql]").forEach(tab => tab.classList.toggle("active", tab === button)); const x = examples[button.dataset.sql];
        $("#sqlStamp").textContent = x.stamp; $("#sqlTitle").textContent = x.title; $("#sqlDescription").textContent = x.desc; $("#sqlGroupLabel").textContent = x.label; $("#sqlNote").textContent = x.note; $("#activeSql").textContent = x.code.replace(/\\n/g, "\n");
    }));
    document.querySelectorAll("[data-copy]").forEach(button => button.addEventListener("click", async () => {
        try { await navigator.clipboard.writeText(document.getElementById(button.dataset.copy)?.textContent || ""); toast("Comando copiado com carinho! ♡") }
        catch { toast("Selecione o comando e copie manualmente.") }
    }));
    const data = {
        alunos: { title: "Alunos", fields: ["id_aluno", "nome_aluno", "email_aluno", "telefone_aluno"] },
        professores: { title: "Professores", fields: ["id_professor", "nome_professor", "email_professor", "especialidade_professor"] },
        cursos: { title: "Cursos", fields: ["id_curso", "nome_curso", "descricao_curso", "cargahoraria_curso"] },
        turmas: { title: "Turmas", fields: ["id_turma", "id_curso", "id_professor", "ano_letivo", "semestre_turma", "turno_turma"] },
        matriculas: { title: "Matrículas", fields: ["id_matricula", "id_aluno", "id_turma", "data_matricula", "situacao_matricula"] },
        notas: { title: "Notas", fields: ["id_nota", "id_matricula", "descricao_nota", "valor_nota", "data_nota"] }
    };
    let current = "alunos", sequence = 0;
    function empty(message) { $("#recordsBody").replaceChildren(); const tr = document.createElement("tr"), td = document.createElement("td"); td.colSpan = data[current].fields.length; td.className = "records-message"; td.textContent = message; tr.append(td); $("#recordsBody").append(tr) }
    function render(response) {
        const fields = data[current].fields, rows = Array.isArray(response) ? response : response?.items || response?.data || [];
        $("#recordsHead").replaceChildren(); $("#recordsBody").replaceChildren();
        const hr = document.createElement("tr"); fields.forEach(field => { const th = document.createElement("th"); th.scope = "col"; th.textContent = field; hr.append(th) }); $("#recordsHead").append(hr);
        if (!rows.length) return empty("A API respondeu sem registros para esta entidade.");
        rows.slice(0, 50).forEach(record => { const tr = document.createElement("tr"); fields.forEach(field => { const td = document.createElement("td"); td.textContent = record?.[field] == null ? "—" : String(record[field]); tr.append(td) }); $("#recordsBody").append(tr) });
    }
    async function load() {
        const id = ++sequence; $("#recordsTitle").textContent = data[current].title; $("#recordsHead").replaceChildren(); empty("Carregando registros…");
        try { const response = await SchoolAPI.get("/" + current); if (id !== sequence) return; render(response); $("#apiStatus").classList.add("online"); $("#apiStatus").querySelector("span:last-child").textContent = "API conectada · consulta de leitura" }
        catch (error) { if (id !== sequence) return; empty(error.message + " Verifique URL e contrato da API."); $("#apiStatus").classList.remove("online"); $("#apiStatus").querySelector("span:last-child").textContent = "API indisponível · sem dados simulados" }
    }
    document.querySelectorAll("[data-resource]").forEach(button => button.addEventListener("click", () => { current = button.dataset.resource; document.querySelectorAll("[data-resource]").forEach(tab => tab.classList.toggle("active", tab === button)); load() }));
    $("#reloadRecords").addEventListener("click", load); load();
})();
