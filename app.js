(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  const date = new Intl.DateTimeFormat("pt-BR", { weekday: "long", day: "numeric", month: "long" });
  const now = new Date();
  $("#todayLabel").textContent = date.format(now);
  $(".eyebrow").textContent = date.format(now).toLocaleUpperCase("pt-BR");
  const names = { inicio: "Início", turmas: "Minhas turmas", atividades: "Atividades", calendario: "Calendário", alunos: "Alunos", professores: "Professores", cursos: "Cursos", matriculas: "Matrículas", notas: "Notas", perfil: "Perfil e preferências" };
  function navigate() {
    const page = location.hash.slice(1) || "inicio";
    const title = names[page] || names.inicio;
    $("#pageCrumb").textContent = title;
    $("#pageTitle").innerHTML = `${escapeHTML(page === "inicio" ? "Olá, que bom ter você por aqui" : title)} <span class="wave">✦</span>`;
    document.querySelectorAll(".nav-link[data-page]").forEach(link => link.classList.toggle("active", link.dataset.page === page));
    const content = $(".content-wrap");
    const placeholder = $("#modulePlaceholder");
    content.querySelectorAll(":scope > :not(.footer-note):not(#modulePlaceholder)").forEach(node => { node.hidden = page !== "inicio"; });
    if (page === "inicio") placeholder?.remove();
    else if (!placeholder) {
      const section = document.createElement("section");
      section.id = "modulePlaceholder";
      section.className = "panel module-placeholder";
      const kicker = document.createElement("span"); kicker.className = "section-kicker"; kicker.textContent = "MÓDULO ESCOLAR";
      const heading = document.createElement("h2"); heading.textContent = title;
      const note = document.createElement("p"); note.textContent = "Esta área ainda não foi implementada. O repositório não contém uma API ou esquema de banco existente para conectar; consulte o README para os contratos e dependências antes de operar dados reais.";
      section.append(kicker, heading, note); content.insertBefore(section, $(".footer-note"));
    } else placeholder.querySelector("h2").textContent = title;
    $("#sidebar").classList.remove("sidebar-open");
    $("#menuToggle").setAttribute("aria-expanded", "false");
  }
  function toast(message) {
    const node = document.createElement("div"); node.className = "toast"; node.textContent = message;
    $("#toastRegion").append(node); setTimeout(() => node.remove(), 4200);
  }
  function showUnavailable(target, label) {
    $(target).innerHTML = `<div class="empty-state"><span class="empty-icon">♡</span><strong>${escapeHTML(label)}</strong><p>Configure o backend em <code>config.js</code> para carregar dados reais. Nenhum dado de exemplo foi inventado.</p></div>`;
  }
  async function load(path, target, label, render) {
    try {
      const data = await SchoolAPI.get(path);
      render(Array.isArray(data) ? data : data?.items || data?.data || []);
    } catch (error) { showUnavailable(target, error.message || label); }
  }
  function renderClasses(items) {
    $("#statTurmas").textContent = items.length;
    if (!items.length) return showUnavailable("#classList", "Nenhuma turma disponível");
    $("#classList").innerHTML = items.slice(0, 4).map((item, i) => `<article class="class-card class-tone-${i % 4}"><div class="class-banner"><span>${escapeHTML(item.nome_curso || item.nome || item.course_name || "Turma")}</span><i>✿</i></div><div class="class-meta"><strong>${escapeHTML(item.nome_turma || item.identificacao || item.semestre_turma || "Turma escolar")}</strong><span>${escapeHTML(item.nome_professor || item.professor || "Professor não informado")}</span></div><div class="class-footer"><span>♙ ${escapeHTML(item.quantidade_alunos ?? item.total_alunos ?? "—")} estudantes</span><a href="#turmas" aria-label="Abrir turma">→</a></div></article>`).join("");
  }
  function renderAgenda(items) {
    $("#statPrazos").textContent = items.length;
    if (!items.length) return showUnavailable("#agendaList", "Sua agenda está livre");
    $("#agendaList").innerHTML = items.slice(0, 3).map(item => `<article class="agenda-item"><span class="agenda-date"><strong>${escapeHTML(item.dia || "—")}</strong><small>${escapeHTML(item.mes || "DATA")}</small></span><span class="agenda-detail"><strong>${escapeHTML(item.titulo || item.nome || "Compromisso")}</strong><small>${escapeHTML(item.nome_curso || item.turma || "Atividade escolar")}</small></span><span class="agenda-dot"></span></article>`).join("");
  }
  function renderActivities(items) {
    $("#statAtividades").textContent = items.length;
    if (!items.length) return showUnavailable("#activityList", "Nenhuma atividade recente");
    $("#activityList").innerHTML = items.slice(0, 4).map(item => `<article class="activity-row"><span class="activity-icon">☷</span><span class="activity-info"><strong>${escapeHTML(item.titulo || item.descricao || "Atividade")}</strong><small>${escapeHTML(item.nome_turma || item.turma || "Turma não informada")}</small></span><span class="activity-deadline">${escapeHTML(item.prazo || item.data_entrega || "Sem prazo")}</span><span class="status-pill">${escapeHTML(item.status || "Disponível")}</span></article>`).join("");
  }
  load("/turmas", "#classList", "Turmas indisponíveis", renderClasses);
  load("/calendario?limit=3", "#agendaList", "Agenda indisponível", renderAgenda);
  load("/atividades?limit=4", "#activityList", "Atividades indisponíveis", renderActivities);
  SchoolAPI.get("/alunos?limit=1").then(data => {
    const items = Array.isArray(data) ? data : data?.items || data?.data || [];
    $("#statAlunos").textContent = data?.total ?? (items[0]?.total ?? items.length);
  }).catch(() => { $("#statAlunos").textContent = "—"; });
  window.addEventListener("hashchange", navigate); navigate();
  $("#menuToggle").addEventListener("click", () => { const open = $("#sidebar").classList.toggle("sidebar-open"); $("#menuToggle").setAttribute("aria-expanded", String(open)); });
  const dialog = $("#actionDialog");
  $("#quickAction").addEventListener("click", () => { $("#dialogTitle").textContent = "Nova turma"; $("#dialogBody").textContent = "A criação de turmas requer uma API autenticada. Configure o backend para continuar."; dialog.showModal(); });
  $("#logoutBtn").addEventListener("click", async () => {
    try { await SchoolAPI.post("/auth/logout", {}); toast("Sessão encerrada."); }
    catch { toast("A autenticação ainda não está configurada no backend."); }
  });
})();
