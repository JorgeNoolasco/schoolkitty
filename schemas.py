"""Validações compartilhadas pelos formulários, executadas antes de gravar."""
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, field_validator


def today() -> date:
    return datetime.now(ZoneInfo('America/Sao_Paulo')).date()


def clean_phone(value):
    return re.sub(r'[\s()+-]', '', value) if isinstance(value, str) else value


def decimal_input(value):
    return value.replace(',', '.') if isinstance(value, str) else value


def date_input(value):
    if isinstance(value, str) and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Informe uma data válida no formato ano-mês-dia.')
    return value


Text100 = Annotated[str, Field(min_length=1, max_length=100)]
Phone = Annotated[str, BeforeValidator(clean_phone), Field(pattern=r'^[0-9]{10,11}$')]
Email = Annotated[EmailStr, Field(max_length=100)]
SchoolDate = Annotated[date, BeforeValidator(date_input), Field(ge=date(1000, 1, 1))]
Identifier = Annotated[int, Field(gt=0, le=2147483647)]


class FormSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')


class AlunoSchema(FormSchema):
    nome_aluno: Text100
    data_nascimento: SchoolDate
    email_aluno: Email
    telefone_aluno: Phone

    @field_validator('data_nascimento')
    @classmethod
    def birth_not_future(cls, value):
        if value > today():
            raise ValueError('O nascimento não pode estar no futuro.')
        return value


class ProfessorSchema(FormSchema):
    nome_professor: Text100
    email_professor: Email
    telefone_professor: Phone
    especialidade_professor: Text100


class CursoSchema(FormSchema):
    nome_curso: Text100
    descricao_curso: Text100
    cargahoraria_curso: Annotated[Decimal, BeforeValidator(decimal_input), Field(gt=0, le=Decimal('99999999.99'), max_digits=10, decimal_places=2)]


class TurmaSchema(FormSchema):
    id_curso: Identifier
    id_professor: Identifier
    ano_letivo: Annotated[int, Field(ge=1900, le=2100)]
    semestre_turma: Annotated[int, Field(ge=1, le=2)]
    turno_turma: Literal['manhã', 'tarde', 'noite']


class MatriculaSchema(FormSchema):
    id_aluno: Identifier
    id_turma: Identifier
    data_matricula: SchoolDate
    situacao_matricula: Literal['ativa', 'concluída', 'cancelada', 'trancada']


class NotaSchema(FormSchema):
    id_matricula: Identifier
    descricao_nota: Text100
    valor_nota: Annotated[Decimal, BeforeValidator(decimal_input), Field(ge=0, le=10, max_digits=4, decimal_places=2)]
    data_nota: SchoolDate
