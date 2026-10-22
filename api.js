/* Cliente HTTP centralizado. Nenhuma conexão ou credencial do MySQL existe no navegador. */
(() => {
  const base = (window.APP_CONFIG?.API_BASE_URL || "/api").replace(/\/$/, "");
  const timeout = window.APP_CONFIG?.REQUEST_TIMEOUT_MS || 10000;
  async function request(path, options = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(`${base}${path}`, {
        ...options, signal: controller.signal, credentials: "include",
        headers: { Accept: "application/json", ...(options.body ? { "Content-Type": "application/json" } : {}), ...options.headers }
      });
      if (!response.ok) {
        let detail = "";
        try { const body = await response.json(); detail = body.detail || body.message || ""; } catch { /* corpo não JSON */ }
        const messages = { 401: "Sua sessão expirou. Entre novamente.", 403: "Você não tem permissão para esta ação.", 404: "Este recurso não foi encontrado.", 422: "Confira os dados informados.", 429: "Muitas solicitações. Tente novamente em instantes." };
        throw new Error(detail || messages[response.status] || (response.status >= 500 ? "A API encontrou um problema." : `Falha na solicitação (${response.status}).`));
      }
      if (response.status === 204) return null;
      return response.json();
    } catch (error) {
      if (error.name === "AbortError") throw new Error("A solicitação demorou demais. Tente novamente.");
      if (error instanceof TypeError) throw new Error("Não foi possível conectar à API escolar.");
      throw error;
    } finally { clearTimeout(timer); }
  }
  window.SchoolAPI = {
    get: path => request(path), post: (path, data) => request(path, { method: "POST", body: JSON.stringify(data) }),
    put: (path, data) => request(path, { method: "PUT", body: JSON.stringify(data) }),
    patch: (path, data) => request(path, { method: "PATCH", body: JSON.stringify(data) }),
    delete: path => request(path, { method: "DELETE" })
  };
})();
