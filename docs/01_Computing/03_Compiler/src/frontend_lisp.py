"""Frontend fuer LISP-artige Syntax (McCarthy 1958-Stil).

Beispiel:

    (defun main ()
      (let ((x 3) (y 4))
        (let ((z (- (+ x y) 1)))
          (print z))))
    (main)

Unterstuetzte S-Expressions:
  * `defun <name> () <body>...`
  * `let ((n1 v1) (n2 v2) ...) body...`
  * `setq <name> <wert>`
  * `(+ a b)`, `(- a b)`
  * `(print x)`
"""
import re

from . import astnodes as A


TOKEN_SPEC = [
    ("COMMENT", r";[^\n]*"),
    ("WS",      r"[ \t\r\n]+"),
    ("LPAREN",  r"\("),
    ("RPAREN",  r"\)"),
    ("NUM",     r"-?\d+"),
    ("SYMBOL",  r"[^\s()]+"),
]
_TOKEN_RE = re.compile(
    "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))


def tokenize(text):
    tokens = []
    pos = 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if not m:
            raise SyntaxError(f"Ungueltiges Zeichen bei Pos {pos}: "
                              f"{text[pos:pos+20]!r}")
        typ, val = m.lastgroup, m.group()
        if typ in ("WS", "COMMENT"):
            pass
        elif typ == "NUM":
            tokens.append(("NUM", int(val)))
        else:
            tokens.append((typ, val))
        pos = m.end()
    tokens.append(("EOF", None))
    return tokens


def parse_sexpr(tokens, pos):
    tok = tokens[pos]
    if tok[0] == "LPAREN":
        elements = []
        pos += 1
        while tokens[pos][0] != "RPAREN":
            if tokens[pos][0] == "EOF":
                raise SyntaxError("Unerwartetes EOF in Liste")
            child, pos = parse_sexpr(tokens, pos)
            elements.append(child)
        return elements, pos + 1
    if tok[0] == "RPAREN":
        raise SyntaxError(f"Unerwartete ')' bei Pos {pos}")
    if tok[0] == "NUM":
        return tok[1], pos + 1
    if tok[0] == "SYMBOL":
        return tok[1], pos + 1
    raise SyntaxError(f"Unerwartetes Token {tok}")


def parse_all(text):
    tokens = tokenize(text)
    trees = []
    pos = 0
    while tokens[pos][0] != "EOF":
        tree, pos = parse_sexpr(tokens, pos)
        trees.append(tree)
    return trees


def _is_num(x): return isinstance(x, int)
def _is_sym(x): return isinstance(x, str)
def _is_list(x): return isinstance(x, list)


def sexpr_to_expr(sx):
    if _is_num(sx):
        return A.Num(sx)
    if _is_sym(sx):
        return A.Var(sx)
    if _is_list(sx):
        if not sx:
            raise SyntaxError("Leere Liste als Ausdruck")
        head = sx[0]
        if head == "+" and len(sx) == 3:
            return A.BinOp("+", sexpr_to_expr(sx[1]), sexpr_to_expr(sx[2]))
        if head == "-" and len(sx) == 3:
            return A.BinOp("-", sexpr_to_expr(sx[1]), sexpr_to_expr(sx[2]))
        raise SyntaxError(f"Unbekannter Ausdruck: {sx}")
    raise SyntaxError(f"Ungueltiger Ausdruck: {sx}")


def sexpr_to_stmts(sx, out):
    if not _is_list(sx) or not sx:
        raise SyntaxError(f"Statement muss Liste sein, ist: {sx}")
    head = sx[0]

    if head == "setq" and len(sx) == 3:
        out.append(A.Assign(sx[1], sexpr_to_expr(sx[2])))
        return

    if head == "let" and len(sx) >= 2:
        for pair in sx[1]:
            if not (_is_list(pair) and len(pair) == 2):
                raise SyntaxError(f"Ungueltiges let-Binding: {pair}")
            out.append(A.Assign(pair[0], sexpr_to_expr(pair[1])))
        for body in sx[2:]:
            sexpr_to_stmts(body, out)
        return

    if head == "print" and len(sx) == 2:
        out.append(A.Output(sexpr_to_expr(sx[1])))
        return

    raise SyntaxError(f"Unbekanntes Statement: {sx}")


def parse(source):
    trees = parse_all(source)

    prog = A.Program(source_language="LISP")
    prog.program_name = "main"

    for form in trees:
        if _is_list(form) and form and form[0] == "defun":
            if len(form) < 4 or form[1] != "main":
                continue
            for stmt in form[3:]:
                sexpr_to_stmts(stmt, prog.statements)
        elif _is_list(form) and form and form[0] == "main":
            pass
        else:
            sexpr_to_stmts(form, prog.statements)

    return prog