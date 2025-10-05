from compiler import ast


class SemanticError(Exception):
    """Excepción específica para errores semánticos (no usada en análisis simple)."""
    pass


def analyze(program_node):
    """Analizador semántico muy simple.

    Recorre el AST y detecta usos de variables antes de su asignación.

    Entrada: nodo Program
    Salida: diccionario con keys:
      - symbols: mapa de nombre -> None (registrados cuando se asignan)
      - errors: lista de mensajes de error semántico
      - ok: booleano si no hay errores
      - message: mensaje resumen
    """
    symbols = {}
    errors = []

    def visit(node):
        # Program: visitar cada sentencia
        if isinstance(node, ast.Program):
            for s in node.statements:
                visit(s)

        # Assign: primero visitar RHS (para detectar usos en la RHS),
        # luego registrar el símbolo como asignado
        elif isinstance(node, ast.Assign):
            visit(node.value)
            symbols[node.name] = None

        # BinOp: visitar subexpresiones
        elif isinstance(node, ast.BinOp):
            visit(node.left)
            visit(node.right)

        # Var: si no fue asignada antes, registrar error
        elif isinstance(node, ast.Var):
            if node.name not in symbols:
                errors.append(f"Variable '{node.name}' usada antes de asignar")

        # Number: literal, no acción necesaria
        elif isinstance(node, ast.Number):
            pass

        else:
            # Nodo desconocido: ignorar para este análisis simple
            pass

    visit(program_node)
    ok = len(errors) == 0
    message = 'Sin errores semánticos' if ok else f'{len(errors)} error(es) semántico(s)'
    return {'symbols': symbols, 'errors': errors, 'ok': ok, 'message': message}
