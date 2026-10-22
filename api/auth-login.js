const crypto = require('node:crypto');
const { issueSession, cookieHeader, configured } = require('../lib/auth');
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ message: 'Método não permitido.' });
  if (!configured(res)) return;
  const username = String(req.body?.username || '').trim();
  const password = String(req.body?.password || '');
  const [scheme, salt, stored] = String(process.env.ADMIN_PASSWORD_HASH).split('$');
  let matches = false;
  if (scheme === 'scrypt' && /^[a-f0-9]{32}$/.test(salt || '') && /^[a-f0-9]{128}$/.test(stored || '')) {
    const actual = crypto.scryptSync(password, salt, 64);
    const expected = Buffer.from(stored, 'hex');
    matches = crypto.timingSafeEqual(actual, expected);
  }
  if (!matches || !crypto.timingSafeEqual(Buffer.from(username.padEnd(256).slice(0, 256)), Buffer.from(String(process.env.ADMIN_USERNAME).padEnd(256).slice(0, 256)))) {
    return res.status(401).json({ message: 'Usuário ou senha inválidos.' });
  }
  res.setHeader('Set-Cookie', cookieHeader(issueSession(username)));
  return res.status(200).json({ username });
};

