from compiler import ast


class ParseNode:
    """Nodo simple para representar el árbol de análisis (parse-tree) usado por la UI.

    - label: etiqueta del nodo (p.ej. 'S', 'E', 'F', 'id', '+')
    - children: lista de ParseNode o valores hoja (strings, números)
    Las funciones to_text y to_text_centered producen representaciones ASCII
    del árbol para mostrar en la interfaz.
    """
    def __init__(self, label, children=None):
        self.label = label
        self.children = children or []

    def to_text(self, indent=0):
        """Representación ASCII vertical con líneas y conectores.

        Produce algo tipo:
        S
        ├─ id
        │  └─ a
        └─ E
           ├─ ...
        """
        # produce ASCII tree with connectors
        def _lines(node, prefix='', is_last=True):
            label = str(node.label)
            connector = '└─ ' if is_last else '├─ '
            lines = [prefix + connector + label]
            # prepare new prefix for children
            if is_last:
                new_prefix = prefix + '   '
            else:
                new_prefix = prefix + '│  '
            for i, c in enumerate(node.children):
                last = (i == len(node.children) - 1)
                if isinstance(c, ParseNode):
                    lines.extend(_lines(c, new_prefix, last))
                else:
                    # leaf value
                    conn = '└─ ' if last else '├─ '
                    lines.append(new_prefix + conn + str(c))
            return lines

        # root has no prefix and should not show connector before root label
        root_lines = [str(self.label)]
        for i, c in enumerate(self.children):
            last = (i == len(self.children) - 1)
            if isinstance(c, ParseNode):
                root_lines.extend(_lines(c, '', last))
            else:
                conn = '└─ ' if last else '├─ '
                root_lines.append(conn + str(c))
        return '\n'.join(root_lines)

    def to_text_centered(self):
        """Construye una representación ASCII con padres centrados sobre los hijos.

        Esta vista es útil para mostrar el árbol sintáctico más 'gráfico' en el UI.
        El algoritmo recursivo calcula anchos y posiciones para alinear etiquetas.
        """
        # returns a centered ASCII-art representation where parent is centered above children
        def build(n):
            label = str(n.label)
            # leaf
            if not n.children:
                w = len(label)
                mid = w // 2
                return [label], w, mid
            # build children
            blocks = []
            for c in n.children:
                if isinstance(c, ParseNode):
                    lines, w, mid = build(c)
                else:
                    txt = str(c)
                    lines, w, mid = [txt], len(txt), len(txt)//2
                blocks.append((lines, w, mid))
            # spacing between blocks
            gap = 3
            total_w = sum(b[1] for b in blocks) + gap * (len(blocks) - 1)
            # position children sequentially
            child_positions = []
            cur = 0
            for lines, w, mid in blocks:
                child_positions.append(cur + mid)
                cur += w + gap
            # center parent label
            parent_mid = total_w // 2
            # compute first line with parent centered
            first = ' ' * max(0, parent_mid - (len(label) // 2)) + label
            # ensure length at least total_w
            if len(first) < total_w:
                first = first + ' ' * (total_w - len(first))
            # second line: vertical bar under parent
            second = list(' ' * total_w)
            second[parent_mid] = '|'
            second = ''.join(second)
            # third line: horizontal connectors from parent to each child position
            third = list(' ' * total_w)
            # draw horizontal line from parent_mid to each child pos
            for pos in child_positions:
                if pos == parent_mid:
                    third[pos] = '+'
                    continue
                start = min(pos, parent_mid)
                end = max(pos, parent_mid)
                for i in range(start, end + 1):
                    third[i] = '-' if third[i] == ' ' else third[i]
                third[pos] = '+'
            third = ''.join(third)
            # now merge children lines
            max_h = max(len(b[0]) for b in blocks)
            child_lines = []
            for i in range(max_h):
                line = []
                for idx, (lines, w, mid) in enumerate(blocks):
                    if i < len(lines):
                        chunk = lines[i]
                    else:
                        chunk = ' ' * w
                    # pad chunk to width w
                    if len(chunk) < w:
                        chunk = chunk + ' ' * (w - len(chunk))
                    line.append(chunk)
                    if idx != len(blocks) - 1:
                        line.append(' ' * gap)
                child_lines.append(''.join(line))
            # assemble all
            out = [first.rstrip(), second.rstrip(), third.rstrip()]
            out.extend(l.rstrip() for l in child_lines)
            return out, max(total_w, len(first)), parent_mid

        lines, _, _ = build(self)
        return '\n'.join(lines)

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, ttype=None):
        tok = self.peek()
        if tok is None:
            return None
        if ttype and tok.type != ttype:
            raise ParserError(f'Expected {ttype} but got {tok.type} at {tok.line}:{tok.col}')
        self.pos += 1
        return tok

    def parse(self):
        # build both AST program and parse-tree S
        stmts = []
        s_root = ParseNode('S')
        while self.peek() is not None:
            if self.peek().type == 'ID' and self.pos+1 < len(self.tokens) and self.tokens[self.pos+1].type == 'ASSIGN':
                a_ast, a_pt = self.parse_assign()
                stmts.append(a_ast)
                s_root.children.append(a_pt)
                if self.peek() and self.peek().type == 'SEMI':
                    self.eat('SEMI')
            else:
                e_ast, e_pt = self.parse_expr()
                stmts.append(e_ast)
                s_root.children.append(e_pt)
                if self.peek() and self.peek().type == 'SEMI':
                    self.eat('SEMI')
        return ast.Program(stmts), s_root

    def parse_assign(self):
        # S -> id = E
        id_tok = self.eat('ID')
        name = id_tok.value
        self.eat('ASSIGN')
        val_ast, val_pt = self.parse_expr()
        # AST
        assign_ast = ast.Assign(name, val_ast)
        # Parse-tree node
        id_node = ParseNode('id', [name])
        eq_node = ParseNode('=', ['='])
        s_node = ParseNode('S', [id_node, eq_node, val_pt])
        return assign_ast, s_node

    def parse_expr(self):
        # parse expression using precedence climbing for binary operators
        return self._parse_precedence()

    def parse_term(self):
        return self.parse_factor()

    def _parse_binary_tail(self, left_ast, left_pt, op_types, node_label, op_symbol_map, right_parse):
        tok = self.peek()
        while tok and tok.type in op_types:
            op_tok = self.eat()
            op = op_tok.type
            # parse right operand using provided callable
            right_ast, right_pt = right_parse()
            left_ast = ast.BinOp(left_ast, op, right_ast)
            op_node = ParseNode(op_symbol_map.get(op, op))
            left_pt = ParseNode(node_label, [left_pt, op_node, right_pt])
            tok = self.peek()
        return left_ast, left_pt

    def _parse_precedence(self):
        """Precedence-climbing parser for binary expressions.

        Returns (ast, parse_node) for an expression E.
        Supports PLUS/MINUS (low precedence) and MUL/DIV (high precedence).
        """
        # define precedences
        prec = {'PLUS': 1, 'MINUS': 1, 'MUL': 2, 'DIV': 2}

        def parse_atom():
            return self.parse_factor()

        def parse_rhs(min_prec, left_ast, left_pt):
            tok = self.peek()
            while tok and tok.type in prec and prec[tok.type] >= min_prec:
                op_tok = self.eat()
                op = op_tok.type
                # parse next atom
                right_ast, right_pt = parse_atom()
                # handle operators of higher precedence that follow
                next_tok = self.peek()
                while next_tok and next_tok.type in prec and prec[next_tok.type] > prec[op]:
                    right_ast, right_pt = parse_rhs(prec[next_tok.type], right_ast, right_pt)
                    next_tok = self.peek()
                # build new left
                left_ast = ast.BinOp(left_ast, op, right_ast)
                symbol = {'PLUS': '+', 'MINUS': '-', 'MUL': '*', 'DIV': '/'}[op]
                left_pt = ParseNode('E', [left_pt, ParseNode(symbol), right_pt])
                tok = self.peek()
            return left_ast, left_pt

        # initial left is an atom
        left_ast, left_pt = parse_atom()
        return parse_rhs(1, left_ast, left_pt)

    def parse_factor(self):
        tok = self.peek()
        if tok.type == 'NUMBER':
            self.eat('NUMBER')
            ast_node = ast.Number(tok.value)
            pt = ParseNode('F', [ParseNode('num', [tok.value])])
            return ast_node, pt
        elif tok.type == 'ID':
            self.eat('ID')
            ast_node = ast.Var(tok.value)
            pt = ParseNode('F', [ParseNode('id', [tok.value])])
            return ast_node, pt
        elif tok.type == 'LPAREN':
            self.eat('LPAREN')
            ast_node, pt = self.parse_expr()
            self.eat('RPAREN')
            # represent (E) as just E in parse-tree but keep grouping
            return ast_node, ParseNode('F', [ParseNode('( )', ['(']), pt, ParseNode('( )', [')'])])
        else:
            raise ParserError(f'Unexpected token {tok.type} at {tok.line}:{tok.col}')



# convenience

def parse(tokens):
    p = Parser(tokens)
    program, parse_root = p.parse()
    return program, parse_root
