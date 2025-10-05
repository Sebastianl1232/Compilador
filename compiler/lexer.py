import re
from collections import namedtuple

# Token es una tupla simple que representa un token lexemizado:
# - type: tipo del token (p.ej. 'NUMBER', 'ID', 'PLUS')
# - value: valor literal (número convertido a int/float, o string)
# - line, col: posición para reportes/errores
Token = namedtuple('Token', ['type', 'value', 'line', 'col'])

# Especificación de tokens: lista de pares (NOMBRE, EXPRESIÓN REGULAR)
# El orden importa: patrones más específicos deben ir antes que patrones generales.
TOKEN_SPEC = [
    ('NUMBER',   r'\d+(?:\.\d+)?'),   # enteros o decimales
    ('ID',       r'[A-Za-z_]\w*'),     # identificadores (letras, dígitos, _)
    ('ASSIGN',   r'='),                 # operador de asignación
    ('PLUS',     r'\+'),               # +
    ('MINUS',    r'-'),                 # -
    ('MUL',      r'\*'),               # *
    ('DIV',      r'/'),                 # /
    ('LPAREN',   r'\('),               # (
    ('RPAREN',   r'\)'),               # )
    ('SEMI',     r';'),                 # ; separador de sentencias
    ('NEWLINE',  r'\n'),               # salto de línea — para tracking de línea/col
    ('SKIP',     r'[ \t]+'),           # espacios y tabs (ignorar)
    ('MISMATCH', r'.'),                 # cualquier otro carácter (error)
]

# Compilar una única expresión regular con grupos con nombre para cada token
TOK_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)


def lex(code):
    """Convierte el texto de entrada en una lista de tokens.

    - Recorre el código con re.finditer usando TOK_REGEX.
    - Convierte literales numéricos a int/float.
    - Mantiene el seguimiento de número de línea y columna para reportes.
    - Lanza RuntimeError en caso de encontrar un carácter inesperado.
    """
    tokens = []
    line_num = 1
    line_start = 0
    for mo in re.finditer(TOK_REGEX, code):
        kind = mo.lastgroup
        value = mo.group()
        col = mo.start() - line_start + 1
        if kind == 'NUMBER':
            # Normalizar número a int o float
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
            tokens.append(Token(kind, value, line_num, col))
        elif kind == 'ID':
            # Identificador
            tokens.append(Token(kind, value, line_num, col))
        elif kind == 'NEWLINE':
            # Actualizar contador de líneas y posición de inicio de línea
            line_num += 1
            line_start = mo.end()
        elif kind == 'SKIP':
            # Ignorar espacios/tabs
            pass
        elif kind == 'MISMATCH':
            # Carácter inesperado -> error léxico
            raise RuntimeError(f'Unexpected character {value!r} at line {line_num} col {col}')
        else:
            # Operadores y símbolos simples
            tokens.append(Token(kind, value, line_num, col))
    return tokens
