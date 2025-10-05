class ASTNode:
    """Clase base para nodos del AST.

    Cada nodo concreto debe implementar to_dict() para serializarse a JSON
    cuando la API REST devuelve la representación del AST.
    """
    def to_dict(self):
        raise NotImplementedError()


class Number(ASTNode):
    """Nodo que representa un literal numérico.

    Atributos:
    - value: int o float
    """
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {'type': 'Number', 'value': self.value}


class Var(ASTNode):
    """Nodo que representa una referencia a una variable (identificador)."""
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {'type': 'Var', 'name': self.name}


class BinOp(ASTNode):
    """Nodo binario (operación entre dos expresiones).

    - left, right: sub-árboles (ASTNode)
    - op: token tipo como 'PLUS', 'MUL', etc. (se usa en evaluator para decidir)
    """
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def to_dict(self):
        return {'type': 'BinOp', 'op': self.op, 'left': self.left.to_dict(), 'right': self.right.to_dict()}


class Assign(ASTNode):
    """Nodo de asignación: name = value"""
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_dict(self):
        return {'type': 'Assign', 'name': self.name, 'value': self.value.to_dict()}


class Program(ASTNode):
    """Nodo raíz que contiene una lista de sentencias del programa."""
    def __init__(self, statements):
        self.statements = statements

    def to_dict(self):
        return {'type': 'Program', 'statements': [s.to_dict() for s in self.statements]}

