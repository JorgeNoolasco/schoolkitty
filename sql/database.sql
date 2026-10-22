-- Execute em MySQL 8.0.16 ou superior. Não apaga bancos nem tabelas existentes.
CREATE DATABASE IF NOT EXISTS escola_hello_kitty CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE escola_hello_kitty;

CREATE TABLE aluno (
    id_aluno INT AUTO_INCREMENT PRIMARY KEY,
    nome_aluno VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    email_aluno VARCHAR(100) NOT NULL,
    telefone_aluno CHAR(11) NOT NULL,
    CONSTRAINT uq_aluno_email UNIQUE (email_aluno),
    INDEX idx_aluno_nome (nome_aluno)
) ENGINE=InnoDB;

CREATE TABLE professor (
    id_professor INT AUTO_INCREMENT PRIMARY KEY,
    nome_professor VARCHAR(100) NOT NULL,
    email_professor VARCHAR(100) NOT NULL,
    telefone_professor CHAR(11) NOT NULL,
    especialidade_professor VARCHAR(100) NOT NULL,
    CONSTRAINT uq_professor_email UNIQUE (email_professor),
    INDEX idx_professor_nome (nome_professor),
    INDEX idx_professor_especialidade (especialidade_professor)
) ENGINE=InnoDB;

CREATE TABLE curso (
    id_curso INT AUTO_INCREMENT PRIMARY KEY,
    nome_curso VARCHAR(100) NOT NULL,
    descricao_curso VARCHAR(100) NOT NULL,
    cargahoraria_curso DECIMAL(10,2) NOT NULL,
    CONSTRAINT ck_curso_horas CHECK (cargahoraria_curso > 0)
) ENGINE=InnoDB;

CREATE TABLE turma (
    id_turma INT AUTO_INCREMENT PRIMARY KEY,
    id_curso INT NOT NULL,
    id_professor INT NOT NULL,
    ano_letivo INT NOT NULL,
    semestre_turma INT NOT NULL,
    turno_turma VARCHAR(20) NOT NULL,
    CONSTRAINT fk_turma_curso FOREIGN KEY (id_curso) REFERENCES curso(id_curso) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_turma_professor FOREIGN KEY (id_professor) REFERENCES professor(id_professor) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT ck_turma_ano CHECK (ano_letivo BETWEEN 1900 AND 2100),
    CONSTRAINT ck_turma_semestre CHECK (semestre_turma IN (1,2)),
    CONSTRAINT ck_turma_turno CHECK (turno_turma IN ('manhã','tarde','noite'))
) ENGINE=InnoDB;

CREATE TABLE matricula (
    id_matricula INT AUTO_INCREMENT PRIMARY KEY,
    id_aluno INT NOT NULL,
    id_turma INT NOT NULL,
    data_matricula DATE NOT NULL,
    situacao_matricula VARCHAR(20) NOT NULL,
    CONSTRAINT fk_matricula_aluno FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_matricula_turma FOREIGN KEY (id_turma) REFERENCES turma(id_turma) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT uq_matricula_aluno_turma UNIQUE (id_aluno,id_turma),
    CONSTRAINT ck_matricula_situacao CHECK (situacao_matricula IN ('ativa','concluída','cancelada','trancada')),
    INDEX idx_matricula_data (data_matricula),
    INDEX idx_matricula_situacao (situacao_matricula)
) ENGINE=InnoDB;

CREATE TABLE nota (
    id_nota INT AUTO_INCREMENT PRIMARY KEY,
    id_matricula INT NOT NULL,
    descricao_nota VARCHAR(100) NOT NULL,
    -- DECIMAL(2,2) não comporta a parte inteira de uma nota 10,00.
    valor_nota DECIMAL(4,2) NOT NULL,
    data_nota DATE NOT NULL,
    CONSTRAINT fk_nota_matricula FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT ck_nota_valor CHECK (valor_nota BETWEEN 0 AND 10)
) ENGINE=InnoDB;

CREATE VIEW vw_alunos_cursos_turmas AS
SELECT a.nome_aluno,c.nome_curso,
       CONCAT('Turma #',t.id_turma,' · ',t.ano_letivo,'/',t.semestre_turma,' · ',t.turno_turma) AS turma
FROM matricula m
JOIN aluno a ON a.id_aluno=m.id_aluno
JOIN turma t ON t.id_turma=m.id_turma
JOIN curso c ON c.id_curso=t.id_curso;
