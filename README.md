
# CompilaLab

Proyecto educativo que implementa un pipeline de compilación mínimo:

- Lexer (tokenización)
- Parser (análisis sintáctico) que produce un "parse-tree" para visualización
- Analizador semántico simple (detección de uso de variables antes de asignar)
- Evaluador (ejecución interpretada)
- Interfaz web (Flask + HTML/JS) para probar y visualizar tokens, árbol sintáctico y análisis semántico

Este repositorio sirve como base para aprender los componentes básicos de un compilador
y para experimentar con la representación visual del parse-tree.

Requisitos
----------

- Python 3.8+ (se probó con 3.10+)
- Virtualenv recomendado

Instalación (Windows / PowerShell)
---------------------------------

1. Crear y activar un entorno virtual:

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Ejecución
---------

Inicia la aplicación Flask (modo desarrollo):

```powershell
set FLASK_APP=app.py; flask run
```

Abre http://127.0.0.1:5000/ en tu navegador.


Estructura del proyecto
-----------------------

- `app.py` — servidor Flask y endpoint `/compile` que integra el pipeline
- `compiler/lexer.py` — tokenizador (función `lex(code)`) 
- `compiler/parser.py` — parser recursivo que devuelve `(Program, ParseNode)`; incluye utilidades para render ASCII
- `compiler/ast.py` — clases de nodos AST (Number, Var, BinOp, Assign, Program)
- `compiler/semantic.py` — análisis semántico simple (uso antes de asignar)
- `compiler/evaluator.py` — evaluador/interpretador del AST
- `templates/index.html`, `static/script.js` — UI estática que consume `/compile`

Uso / Ejemplo
-------------

Escribe en el textarea código como:

```text
a = 1 + 2 * (3 + 4);
b = a - 5;
```

Al pulsar "Compilar" verás en el panel:
- Análisis Léxico: tokens detectados (con etiquetas en español)
- Análisis Sintáctico: árbol (ASCII) centrado, o la serialización del AST si no hay parse-tree
- Análisis Semántico: símbolos detectados y errores (uso antes de asignar)
- Validaciones: badges que indican el estado léxico/sintáctico/semántico

Notas técnicas y cambios recientes
---------------------------------

- Parser: se refactorizó a un algoritmo de "precedence-climbing" (climbing precedence) para manejar
  operadores binarios con diferentes precedencias (+,- vs *,/). Esto simplifica la lógica
  en `compiler/parser.py` y reduce duplicación.
- Parse-tree: además del AST, el parser construye un `ParseNode` que se renderiza en ASCII
  con `to_text()` y `to_text_centered()` para mostrar un árbol centrado en la UI.
- UI: paletas de colores suaves que rotan automáticamente y se guardan en `localStorage`; el
  árbol sintáctico se centra dentro del recuadro grande para facilitar su lectura.


