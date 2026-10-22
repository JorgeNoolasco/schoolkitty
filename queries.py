"""Consultas fixas com filtros parametrizados."""

REPORTS = {'alunos': {'title': 'Todos os alunos',
            'sql': 'SELECT id_aluno AS ID,nome_aluno AS Aluno,data_nascimento AS '
                   'Nascimento,email_aluno AS Email,telefone_aluno AS Telefone FROM aluno ORDER BY '
                   'nome_aluno',
            'filter_kind': None},
 'professores': {'title': 'Professores e suas turmas',
                 'sql': 'SELECT p.nome_professor AS Professor,p.especialidade_professor AS '
                        'Especialidade,t.id_turma AS Turma,c.nome_curso AS Curso,t.ano_letivo AS '
                        'Ano,t.semestre_turma AS Semestre,t.turno_turma AS Turno FROM professor p '
                        'LEFT JOIN turma t USING(id_professor) LEFT JOIN curso c USING(id_curso) '
                        'ORDER BY p.nome_professor',
                 'filter_kind': None},
 'cursos': {'title': 'Cursos disponíveis',
            'sql': 'SELECT nome_curso AS Curso,descricao_curso AS Descrição,cargahoraria_curso AS '
                   'Horas FROM curso ORDER BY nome_curso',
            'filter_kind': None},
 'turma': {'title': 'Alunos por turma',
           'sql': 'SELECT a.nome_aluno AS Aluno,c.nome_curso AS Curso,t.id_turma AS '
                  'Turma,m.situacao_matricula AS Situação FROM matricula m JOIN aluno a '
                  'USING(id_aluno) JOIN turma t USING(id_turma) JOIN curso c USING(id_curso) WHERE '
                  'm.id_turma = :filter_value ORDER BY a.nome_aluno',
           'filter_kind': 'turmas'},
 'notas': {'title': 'Notas de um aluno',
           'sql': 'SELECT a.nome_aluno AS Aluno,c.nome_curso AS Curso,t.id_turma AS '
                  'Turma,n.descricao_nota AS Avaliação,n.valor_nota AS Nota,n.data_nota AS Data '
                  'FROM nota n JOIN matricula m USING(id_matricula) JOIN aluno a USING(id_aluno) '
                  'JOIN turma t USING(id_turma) JOIN curso c USING(id_curso) WHERE a.id_aluno = '
                  ':filter_value ORDER BY n.data_nota DESC',
           'filter_kind': 'alunos'},
 'medias': {'title': 'Média por matrícula',
            'sql': 'SELECT m.id_matricula AS Matrícula,a.nome_aluno AS Aluno,c.nome_curso AS '
                   'Curso,t.id_turma AS Turma,COUNT(n.id_nota) AS '
                   'Avaliações,ROUND(AVG(n.valor_nota),2) AS Média FROM matricula m JOIN aluno a '
                   'USING(id_aluno) JOIN turma t USING(id_turma) JOIN curso c USING(id_curso) LEFT '
                   'JOIN nota n USING(id_matricula) GROUP BY '
                   'm.id_matricula,a.nome_aluno,c.nome_curso,t.id_turma ORDER BY a.nome_aluno',
            'filter_kind': None},
 'quantidade': {'title': 'Quantidade de alunos por turma',
                'sql': 'SELECT t.id_turma AS Turma,c.nome_curso AS Curso,t.ano_letivo AS '
                       'Ano,t.semestre_turma AS Semestre,t.turno_turma AS Turno,COUNT(m.id_aluno) '
                       'AS Alunos FROM turma t JOIN curso c USING(id_curso) LEFT JOIN matricula m '
                       'USING(id_turma) GROUP BY '
                       't.id_turma,c.nome_curso,t.ano_letivo,t.semestre_turma,t.turno_turma',
                'filter_kind': None},
 'situacao': {'title': 'Matrículas por situação',
              'sql': 'SELECT m.id_matricula AS Matrícula,a.nome_aluno AS Aluno,c.nome_curso AS '
                     'Curso,t.id_turma AS Turma,m.data_matricula AS Data,m.situacao_matricula AS '
                     'Situação FROM matricula m JOIN aluno a USING(id_aluno) JOIN turma t '
                     'USING(id_turma) JOIN curso c USING(id_curso) WHERE m.situacao_matricula = '
                     ':filter_value ORDER BY a.nome_aluno',
              'filter_kind': 'situacao'},
 'view': {'title': 'View: alunos, cursos e turmas',
          'sql': 'SELECT nome_aluno AS Aluno,nome_curso AS Curso,turma AS Turma FROM '
                 'vw_alunos_cursos_turmas ORDER BY nome_aluno',
          'filter_kind': None}}

RELATION_QUERIES = {'alunos': 'SELECT id_aluno AS id, nome_aluno AS label FROM aluno ORDER BY nome_aluno',
 'professores': 'SELECT id_professor AS id, nome_professor AS label FROM professor ORDER BY '
                'nome_professor',
 'cursos': 'SELECT id_curso AS id, nome_curso AS label FROM curso ORDER BY nome_curso',
 'turmas': "SELECT t.id_turma AS id, CONCAT('#',t.id_turma,' · ',c.nome_curso,' · "
           "',t.ano_letivo,'/',t.semestre_turma,' · ',t.turno_turma) AS label FROM turma t JOIN "
           'curso c USING(id_curso) ORDER BY t.id_turma DESC',
 'matriculas': "SELECT m.id_matricula AS id, CONCAT(a.nome_aluno,' · ',c.nome_curso,' · turma "
               "#',t.id_turma,' · ',t.ano_letivo,'/',t.semestre_turma,' · ',t.turno_turma) AS "
               'label FROM matricula m JOIN aluno a USING(id_aluno) JOIN turma t USING(id_turma) '
               'JOIN curso c USING(id_curso) ORDER BY a.nome_aluno'}
