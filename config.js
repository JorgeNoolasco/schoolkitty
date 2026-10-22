// Configure a URL pública da API em index.html antes de config.js, se necessário.
// Mesmo domínio: /api. Projeto separado: https://seu-backend.vercel.app/api
window.APP_CONFIG = window.APP_CONFIG || { API_BASE_URL: "/api", REQUEST_TIMEOUT_MS: 10000 };
