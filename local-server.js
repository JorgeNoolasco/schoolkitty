const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { URL } = require('node:url');
const { readCookie, validSession } = require('./lib/auth');
const root = __dirname;
const mime = { '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.svg':'image/svg+xml', '.json':'application/json; charset=utf-8' };
const routes = {
  '/api/auth-login': require('./api/auth-login'),
  '/api/auth-logout': require('./api/auth-logout'),
  '/api/auth-session': require('./api/auth-session'),
  '/api/school': require('./api/school')
};
function loadLocalEnv() {
  const filename = path.join(root, '.env.local');
  if (!fs.existsSync(filename)) return;
  for (const line of fs.readFileSync(filename, 'utf8').split(/\r?\n/)) {
    const match = line.match(/^([A-Z][A-Z0-9_]*)=(.*)$/);
    if (match && process.env[match[1]] === undefined) process.env[match[1]] = match[2].replace(/^['"]|['"]$/g, '');
  }
}
loadLocalEnv();
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  if (url.pathname === '/painel.html' && !validSession(readCookie(req))) {
    res.writeHead(302, { Location: '/login.html', 'Cache-Control':'no-store' }); return res.end();
  }
  if (routes[url.pathname]) {
    let body = '';
    for await (const chunk of req) body += chunk;
    try { req.body = body ? JSON.parse(body) : {}; } catch { res.writeHead(400, {'Content-Type':mime['.json']}); return res.end(JSON.stringify({message:'Corpo JSON inválido.'})); }
    req.query = Object.fromEntries(url.searchParams.entries());
    res.status = code => { res.statusCode = code; return res; };
    res.json = value => { res.setHeader('Content-Type', mime['.json']); res.end(JSON.stringify(value)); return res; };
    try { await routes[url.pathname](req, res); }
    catch { if (!res.writableEnded) { res.statusCode = 500; res.setHeader('Content-Type', mime['.json']); res.end(JSON.stringify({message:'Erro interno do servidor.'})); } }
    return;
  }
  const requested = url.pathname === '/' ? '/index.html' : decodeURIComponent(url.pathname);
  const filename = path.resolve(root, `.${requested}`);
  if (!filename.startsWith(root + path.sep) || !fs.existsSync(filename) || !fs.statSync(filename).isFile()) { res.writeHead(404); return res.end('Not found'); }
  res.writeHead(200, { 'Content-Type':mime[path.extname(filename)] || 'application/octet-stream', 'X-Content-Type-Options':'nosniff' });
  fs.createReadStream(filename).pipe(res);
});
const port = Number(process.env.PORT || 3000);
server.listen(port, '127.0.0.1', () => console.log(`Escola Kawaii local: http://127.0.0.1:${port}`));
