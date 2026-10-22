-- Material didático. Execute somente os trechos desejados no Workbench.
USE escola_hello_kitty;

-- DQL: consultas que não alteram registros.
SELECT * FROM aluno ORDER BY nome_aluno;
SELECT p.nome_professor,t.id_turma,t.ano_letivo,t.turno_turma FROM professor p LEFT JOIN turma t USING(id_professor);
SELECT * FROM curso;
SET @turma = 1;
SELECT a.nome_aluno,m.situacao_matricula FROM matricula m JOIN aluno a USING(id_aluno) WHERE m.id_turma=@turma;
SET @aluno = 1;
SELECT a.nome_aluno,c.nome_curso,t.id_turma,n.descricao_nota,n.valor_nota FROM nota n JOIN matricula m USING(id_matricula) JOIN aluno a USING(id_aluno) JOIN turma t USING(id_turma) JOIN curso c USING(id_curso) WHERE a.id_aluno=@aluno;
SELECT m.id_matricula,ROUND(AVG(n.valor_nota),2) AS media FROM matricula m LEFT JOIN nota n USING(id_matricula) GROUP BY m.id_matricula;
SELECT t.id_turma,COUNT(m.id_matricula) AS alunos FROM turma t LEFT JOIN matricula m USING(id_turma) GROUP BY t.id_turma;
SELECT situacao_matricula,COUNT(*) AS quantidade FROM matricula GROUP BY situacao_matricula;
SELECT * FROM vw_alunos_cursos_turmas;

-- Exemplos mutáveis ficam comentados para evitar execução acidental.
-- DDL: cria uma tabela de exemplo separada da modelagem da escola.
-- CREATE TABLE exemplo_aula (id INT AUTO_INCREMENT PRIMARY KEY, descricao VARCHAR(100) NOT NULL) ENGINE=InnoDB;

-- DML: executar em uma transação permite desfazer a demonstração.
-- START TRANSACTION;
-- INSERT INTO aluno (nome_aluno,data_nascimento,email_aluno,telefone_aluno)
-- VALUES ('Aluno Exemplo','2007-01-01','exemplo@example.com','11900000999');
-- SET @novo_aluno = LAST_INSERT_ID();
-- UPDATE aluno SET nome_aluno='Aluno Atualizado' WHERE id_aluno=@novo_aluno;
-- DELETE FROM aluno WHERE id_aluno=@novo_aluno;
-- ROLLBACK;

-- DCL: executar manualmente como administrador, escolhendo uma senha própria.
-- CREATE USER 'escola_app'@'localhost' IDENTIFIED BY 'SUBSTITUA_POR_UMA_SENHA_FORTE';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON escola_hello_kitty.* TO 'escola_app'@'localhost';
-- SHOW GRANTS FOR 'escola_app'@'localhost';
-- REVOKE DELETE ON escola_hello_kitty.* FROM 'escola_app'@'localhost';
