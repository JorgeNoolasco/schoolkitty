const { readCookie, validSession } = require('../lib/auth');
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ message: 'Método não permitido.' });
  res.setHeader('Set-Cookie', 'school_session=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0');
  return res.status(200).json({ ok: true });
};

