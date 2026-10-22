-- Dados exclusivamente fictícios. Execute uma vez, após criar as tabelas vazias.
USE escola_hello_kitty;
START TRANSACTION;
INSERT INTO aluno (id_aluno,nome_aluno,data_nascimento,email_aluno,telefone_aluno) VALUES
(1,'Ana Flor','2007-03-12','ana.flor@example.com','11900000001'),
(2,'Beatriz Rosa','2006-07-22','beatriz.rosa@example.com','11900000002'),
(3,'Caio Luz','2008-01-05','caio.luz@example.com','11900000003'),
(4,'Diana Campos','2007-11-19','diana.campos@example.com','11900000004'),
(5,'Enzo Sol','2006-04-08','enzo.sol@example.com','11900000005'),
(6,'Flora Lima','2008-09-23','flora.lima@example.com','11900000006'),
(7,'Gabriel Vale','2007-06-15','gabriel.vale@example.com','11900000007'),
(8,'Helena Alves','2006-12-30','helena.alves@example.com','11900000008'),
(9,'Igor Melo','2008-02-11','igor.melo@example.com','11900000009'),
(10,'Júlia Nunes','2007-08-17','julia.nunes@example.com','11900000010');
INSERT INTO professor (id_professor,nome_professor,email_professor,telefone_professor,especialidade_professor) VALUES
(1,'Clara Jardim','clara.jardim@example.com','11900000101','Tecnologia'),
(2,'Lucas Prado','lucas.prado@example.com','11900000102','Design'),
(3,'Marina Costa','marina.costa@example.com','11900000103','Gestão'),
(4,'Pedro Neves','pedro.neves@example.com','11900000104','Tecnologia'),
(5,'Sofia Freitas','sofia.freitas@example.com','11900000105','Idiomas');
INSERT INTO curso (id_curso,nome_curso,descricao_curso,cargahoraria_curso) VALUES
(1,'Desenvolvimento Web','Fundamentos de HTML, CSS, JavaScript e PHP',160),
(2,'Design Digital','Comunicação visual e criação digital',120),
(3,'Administração','Fundamentos de gestão e organização',100),
(4,'Banco de Dados','Modelagem relacional e consultas SQL',80),
(5,'Inglês Instrumental','Leitura e comunicação para tecnologia',60);
INSERT INTO turma (id_turma,id_curso,id_professor,ano_letivo,semestre_turma,turno_turma) VALUES
(1,1,1,2026,2,'manhã'),(2,2,2,2026,2,'tarde'),(3,3,3,2026,2,'noite'),(4,4,4,2026,2,'manhã'),(5,5,5,2026,2,'tarde');
INSERT INTO matricula (id_matricula,id_aluno,id_turma,data_matricula,situacao_matricula) VALUES
(1,1,1,'2026-07-10','ativa'),(2,2,2,'2026-07-11','ativa'),(3,3,3,'2026-07-12','ativa'),
(4,4,4,'2026-07-13','ativa'),(5,5,5,'2026-07-14','concluída'),(6,6,1,'2026-07-15','ativa'),
(7,7,2,'2026-07-16','trancada'),(8,8,3,'2026-07-17','ativa'),(9,9,4,'2026-07-18','cancelada'),(10,10,5,'2026-07-19','ativa');
INSERT INTO nota (id_matricula,descricao_nota,valor_nota,data_nota) VALUES
(1,'Atividade prática',8.50,'2026-08-10'),(1,'Projeto',9.00,'2026-09-12'),
(2,'Atividade prática',7.50,'2026-08-10'),(2,'Projeto',8.00,'2026-09-12'),
(3,'Atividade prática',9.00,'2026-08-10'),(3,'Projeto',8.50,'2026-09-12'),
(4,'Atividade prática',10.00,'2026-08-10'),(4,'Projeto',9.50,'2026-09-12'),
(5,'Atividade prática',7.00,'2026-08-10'),(5,'Projeto',8.00,'2026-09-12'),
(6,'Atividade prática',8.50,'2026-08-10'),(7,'Atividade prática',6.50,'2026-08-10'),
(8,'Atividade prática',9.00,'2026-08-10'),(9,'Atividade prática',7.50,'2026-08-10'),(10,'Atividade prática',10.00,'2026-08-10');
COMMIT;
