const crypto = require('node:crypto');
const COOKIE = 'school_session';
function sign(value) {
  return crypto.createHmac('sha256', process.env.SESSION_SECRET).update(value).digest('base64url');
}
function issueSession(username) {
  const payload = Buffer.from(JSON.stringify({ sub: username, exp: Date.now() + 60 * 60 * 1000 })).toString('base64url');
  return `${payload}.${sign(payload)}`;
}
function validSession(token) {
  if (!process.env.SESSION_SECRET || !token) return false;
  const [payload, signature] = token.split('.');
  if (!payload || !signature) return false;
  const expected = sign(payload);
  const a = Buffer.from(signature), b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return false;
  try { const session = JSON.parse(Buffer.from(payload, 'base64url').toString()); return session.exp > Date.now() && session.sub === process.env.ADMIN_USERNAME; }
  catch { return false; }
}
function cookieHeader(token, maxAge = 3600) {
  return `${COOKIE}=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAge}`;
}
function readCookie(req) {
  const raw = req.headers.cookie || '';
  return raw.split(';').map(part => part.trim()).find(part => part.startsWith(`${COOKIE}=`))?.slice(COOKIE.length + 1);
}
function configured(res) {
  if (process.env.ADMIN_USERNAME && process.env.ADMIN_PASSWORD_HASH && Buffer.byteLength(process.env.SESSION_SECRET || '', 'utf8') >= 32) return true;
  res.status(503).json({ message: 'Autenticação ainda não configurada neste ambiente.' });
  return false;
}
module.exports = { issueSession, validSession, cookieHeader, readCookie, configured };
