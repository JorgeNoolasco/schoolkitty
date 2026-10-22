-- Migração aditiva para recursos do Classroom. Requer MySQL 8.0.16+.
-- Faça backup antes de aplicar. Nenhuma tabela ou registro existente é removido.
USE escola_hello_kitty;

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    perfil VARCHAR(20) NOT NULL,
    id_aluno INT NULL,
    id_professor INT NULL,
    ativo TINYINT NOT NULL DEFAULT 1,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_usuario_email UNIQUE (email),
    CONSTRAINT uq_usuario_aluno UNIQUE (id_aluno),
    CONSTRAINT uq_usuario_professor UNIQUE (id_professor),
    CONSTRAINT fk_usuario_aluno FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno) ON DELETE RESTRICT,
    CONSTRAINT fk_usuario_professor FOREIGN KEY (id_professor) REFERENCES professor(id_professor) ON DELETE RESTRICT,
    CONSTRAINT ck_usuario_perfil CHECK (perfil IN ('administrador','professor','aluno')),
    CONSTRAINT ck_usuario_vinculo_perfil CHECK (
      (perfil = 'administrador' AND id_aluno IS NULL AND id_professor IS NULL) OR
      (perfil = 'aluno' AND id_aluno IS NOT NULL AND id_professor IS NULL) OR
      (perfil = 'professor' AND id_professor IS NOT NULL AND id_aluno IS NULL)
    ),
    CONSTRAINT ck_usuario_ativo CHECK (ativo IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE atividade (
    id_atividade INT AUTO_INCREMENT PRIMARY KEY,
    id_turma INT NOT NULL,
    id_professor INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT NOT NULL,
    instrucoes TEXT NOT NULL,
    publicada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_entrega DATETIME NOT NULL,
    pontuacao_maxima DECIMAL(7,2) NOT NULL,
    CONSTRAINT fk_atividade_turma FOREIGN KEY (id_turma) REFERENCES turma(id_turma) ON DELETE RESTRICT,
    CONSTRAINT fk_atividade_professor FOREIGN KEY (id_professor) REFERENCES professor(id_professor) ON DELETE RESTRICT,
    CONSTRAINT ck_atividade_pontos CHECK (pontuacao_maxima > 0 AND pontuacao_maxima <= 1000),
    INDEX idx_atividade_entrega (id_turma, data_entrega)
) ENGINE=InnoDB;

CREATE TABLE entrega_atividade (
    id_entrega INT AUTO_INCREMENT PRIMARY KEY,
    id_atividade INT NOT NULL,
    id_aluno INT NOT NULL,
    resposta TEXT NOT NULL,
    entregue_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nota DECIMAL(7,2) NULL,
    feedback TEXT NULL,
    avaliada_em DATETIME NULL,
    CONSTRAINT fk_entrega_atividade FOREIGN KEY (id_atividade) REFERENCES atividade(id_atividade) ON DELETE RESTRICT,
    CONSTRAINT fk_entrega_aluno FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno) ON DELETE RESTRICT,
    CONSTRAINT uq_entrega_atividade_aluno UNIQUE (id_atividade, id_aluno),
    CONSTRAINT ck_entrega_nota_nao_negativa CHECK (nota IS NULL OR nota >= 0),
    INDEX idx_entrega_aluno (id_aluno, entregue_em)
) ENGINE=InnoDB;

CREATE TABLE aviso (
    id_aviso INT AUTO_INCREMENT PRIMARY KEY,
    id_turma INT NOT NULL,
    id_professor INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    mensagem TEXT NOT NULL,
    publicado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_aviso_turma FOREIGN KEY (id_turma) REFERENCES turma(id_turma) ON DELETE RESTRICT,
    CONSTRAINT fk_aviso_professor FOREIGN KEY (id_professor) REFERENCES professor(id_professor) ON DELETE RESTRICT,
    INDEX idx_aviso_turma_data (id_turma, publicado_em)
) ENGINE=InnoDB;

CREATE TABLE evento_calendario (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    id_turma INT NULL,
    id_criador INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT NULL,
    inicio_em DATETIME NOT NULL,
    fim_em DATETIME NULL,
    CONSTRAINT fk_evento_turma FOREIGN KEY (id_turma) REFERENCES turma(id_turma) ON DELETE RESTRICT,
    CONSTRAINT fk_evento_usuario FOREIGN KEY (id_criador) REFERENCES usuario(id_usuario) ON DELETE RESTRICT,
    CONSTRAINT ck_evento_intervalo CHECK (fim_em IS NULL OR fim_em >= inicio_em),
    INDEX idx_evento_data (inicio_em)
) ENGINE=InnoDB;
