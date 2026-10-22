const mysql = require('mysql2/promise');
const { readCookie, validSession, configured } = require('../lib/auth');
const resources = {
  alunos: ['id_aluno', 'nome_aluno', 'email_aluno', 'telefone_aluno'],
  professores: ['id_professor', 'nome_professor', 'email_professor', 'especialidade_professor'],
  cursos: ['id_curso', 'nome_curso', 'descricao_curso', 'cargahoraria_curso'],
  turmas: ['id_turma', 'id_curso', 'id_professor', 'ano_letivo', 'semestre_turma', 'turno_turma'],
  matriculas: ['id_matricula', 'id_aluno', 'id_turma', 'data_matricula', 'situacao_matricula'],
  notas: ['id_nota', 'id_matricula', 'descricao_nota', 'valor_nota', 'data_nota']
};
const dbOptions = () => ({
  host: process.env.DB_HOST, port: Number(process.env.DB_PORT || 3306),
  user: process.env.DB_USER, password: process.env.DB_PASSWORD, database: process.env.DB_NAME,
  connectTimeout: 8000, ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: true } : undefined
});
module.exports = async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ message: 'Método não permitido.' });
  if (!configured(res)) return;
  if (!validSession(readCookie(req))) return res.status(401).json({ message: 'Autenticação necessária.' });
  if (!process.env.DB_HOST || !process.env.DB_USER || !process.env.DB_NAME) return res.status(503).json({ message: 'Banco de dados não configurado neste ambiente.' });
  const resource = String(req.query.resource || '');
  const isSummary = resource === 'resumo';
  const isView = resource === 'vw_alunos_cursos_turmas';
  if (!resources[resource] && !isSummary && !isView) return res.status(404).json({ message: 'Recurso não encontrado.' });
  let db;
  try {
    db = await mysql.createConnection(dbOptions());
    let rows;
    if (isSummary) {
      const [data] = await db.query('SELECT (SELECT COUNT(*) FROM aluno) AS alunos, (SELECT COUNT(*) FROM professor) AS professores, (SELECT COUNT(*) FROM curso) AS cursos, (SELECT COUNT(*) FROM turma) AS turmas');
      rows = data[0];
    } else if (isView) {
      const [data] = await db.query('SELECT nome_aluno, nome_curso, identificacao_turma FROM vw_alunos_cursos_turmas LIMIT 100');
      rows = data;
    } else {
      const fields = resources[resource].map(field => `\`${field}\``).join(', ');
      const table = { alunos: 'aluno', professores: 'professor', cursos: 'curso', turmas: 'turma', matriculas: 'matricula', notas: 'nota' }[resource];
      const [data] = await db.query(`SELECT ${fields} FROM \`${table}\` LIMIT 100`);
      rows = data;
    }
    res.setHeader('Cache-Control', 'private, no-store');
    return res.status(200).json(rows);
  } catch (error) {
    console.error('School database query failed:', error.code || 'unknown');
    return res.status(503).json({ message: 'Não foi possível consultar os dados escolares. Confira a conexão e o esquema do banco.' });
  } finally { if (db) await db.end(); }
};

