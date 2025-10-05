from compiler import ast


class Evaluator:
    """Evaluador simple que recorre el AST y calcula valores.

    - Mantiene un diccionario `env` que asocia nombres de variables a valores.
    - Evalúa Program, Assign, Number, Var y BinOp.
    - Var devuelve 0 por defecto si la variable no existe (comportamiento simple
      para evitar excepciones en demos).
    """
    def __init__(self):
        # entorno de ejecución: nombre -> valor
        self.env = {}

    def eval(self, node):
        # Program: evaluar cada sentencia y retornar lista de resultados
        if isinstance(node, ast.Program):
            results = []
            for s in node.statements:
                results.append(self.eval(s))
            return results

        # Assign: evaluar RHS y guardar en el entorno
        if isinstance(node, ast.Assign):
            value = self.eval(node.value)
            self.env[node.name] = value
            return value

        # Number: literal numérico
        if isinstance(node, ast.Number):
            return node.value

        # Var: recuperar valor de la variable (0 por defecto)
        if isinstance(node, ast.Var):
            return self.env.get(node.name, 0)

        # BinOp: evaluar subexpresiones y aplicar operador
        if isinstance(node, ast.BinOp):
            l = self.eval(node.left)
            r = self.eval(node.right)
            if node.op == 'PLUS':
                return l + r
            if node.op == 'MINUS':
                return l - r
            if node.op == 'MUL':
                return l * r
            if node.op == 'DIV':
                return l / r

        # Nodo desconocido -> error en tiempo de ejecución
        raise RuntimeError('Unknown node')


def evaluate(ast_node):
    """Función de conveniencia que crea un Evaluator y evalúa el AST dado."""
    ev = Evaluator()
    return ev.eval(ast_node)
