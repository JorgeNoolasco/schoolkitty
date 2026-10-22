const { readCookie, validSession, configured } = require('../lib/auth');
module.exports = async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ message: 'Método não permitido.' });
  if (!configured(res)) return;
  if (!validSession(readCookie(req))) return res.status(401).json({ message: 'Autenticação necessária.' });
  return res.status(200).json({ authenticated: true, username: process.env.ADMIN_USERNAME });
};

