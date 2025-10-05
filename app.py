from flask import Flask, render_template, request, jsonify
from compiler import lexer, parser, evaluator, semantic
import traceback

app = Flask(__name__)


@app.route('/')
def index():
    # Página principal que sirve la plantilla HTML (UI)
    return render_template('index.html')


@app.route('/compile', methods=['POST'])
def compile_code():
    """Endpoint que recibe el código del cliente, lo compila y devuelve

    Resumen del flujo:
    1. LEX: tokenizar con lexer.lex
    2. PARSE: construir AST y parse-tree usando parser.parse
    3. SEMANTIC: análisis semántico simple (uso antes de asignar)
    4. EVALUATE: si no hay errores semánticos, evaluar el AST
    5. Construir respuesta JSON con tokens, representación legible (lex),
       AST serializada, texto del parse-tree y resultados/validaciones.
    """
    code = request.json.get('code', '')
    try:
        # LEXICAL: convertir texto a tokens
        tokens = lexer.lex(code)
        validation = {
            'lexical': {'ok': True, 'message': f'{len(tokens)} token(s) generados' if tokens else '0 tokens'}
        }

        # SYNTACTIC: parsear tokens -> AST + parse-tree
        try:
            parsed = parser.parse(tokens)
            # parser.parse devuelve (program, parse_root)
            if isinstance(parsed, tuple):
                ast_node, parse_root = parsed
            else:
                ast_node = parsed
                parse_root = None
            validation['syntactic'] = {'ok': True, 'message': 'Parseo correcto'}
        except Exception as pe:
            # Capturar error de parseo y continuar para devolver información útil
            ast_node = None
            parse_root = None
            validation['syntactic'] = {'ok': False, 'message': str(pe)}

        # SEMANTIC: sólo si el parse fue correcto
        if validation.get('syntactic', {}).get('ok'):
            semantic_res = semantic.analyze(ast_node)
            validation['semantic'] = {'ok': semantic_res.get('ok', False), 'message': semantic_res.get('message', '')}
        else:
            semantic_res = {'symbols': {}, 'errors': ['Parse error, análisis semántico omitido'], 'ok': False, 'message': 'Omitido'}
            validation['semantic'] = {'ok': False, 'message': 'Omitido por error sintáctico'}

        # EVALUATION: si hay errores semánticos no evaluamos
        if semantic_res.get('errors'):
            result = None
        else:
            result = evaluator.evaluate(ast_node)

        # Mapeo para etiquetas legibles en español y reconocimiento de keywords
        def token_label(tok):
            t = tok.type
            v = tok.value
            # detectar 'keywords' simples (si se decide introducirlas)
            if t == 'ID' and isinstance(v, str) and v in ('let', 'var', 'const'):
                return ('declare', v)
            if t == 'ID':
                return ('identificador', v)
            if t == 'NUMBER':
                return ('number', v)
            if t in ('ASSIGN', 'PLUS', 'MINUS', 'MUL', 'DIV'):
                return ('operador', v)
            if t in ('LPAREN', 'RPAREN'):
                return ('paren', v)
            if t == 'SEMI':
                return ('separador', v)
            return (t.lower(), v)

        lex_display = [f"[{lbl}: {val}]" for (lbl, val) in (token_label(t) for t in tokens)]

        # Intentar producir ambas formas de texto del parse-tree (vertical y centrado)
        parse_text = None
        try:
            parse_text = parse_root.to_text(0) if parse_root and hasattr(parse_root, 'to_text') else None
        except Exception:
            parse_text = None
        parse_text_centered = None
        try:
            parse_text_centered = parse_root.to_text_centered() if parse_root and hasattr(parse_root, 'to_text_centered') else None
        except Exception:
            parse_text_centered = None

        return jsonify({
            'ok': True,
            'tokens': [t._asdict() for t in tokens],
            'lex': lex_display,
            'ast': ast_node.to_dict() if ast_node else None,
            'parse_text': parse_text,
            'parse_text_centered': parse_text_centered,
            'result': result,
            'semantic': semantic_res,
            'validation': validation
        })
    except Exception as e:
        # Error inesperado: devolver traza para depuración en el frontend
        return jsonify({'ok': False, 'error': str(e), 'trace': traceback.format_exc()}), 400


if __name__ == '__main__':
    app.run(debug=True)
