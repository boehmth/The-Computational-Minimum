"""Frontend fuer FORTRAN-artige Syntax (FORTRAN IV/77-Stil).

Beispiel:

          PROGRAM ARITHMETIK
          IMPLICIT NONE
          INTEGER X, Y, Z
    C     -- Berechnung --
              X = 3
              Y = 4
              Z = X + Y - 1
              WRITE(*,*) Z
          STOP
          END PROGRAM

Historische Besonderheiten (rein syntaktisch akzeptiert):
  * PROGRAM name
  * IMPLICIT NONE
  * INTEGER x, y, z  (Typ-Deklaration)
  * C ... oder * ... als Zeilenkommentar
  * ! als moderner Kommentar
  * WRITE(*,*) expr
  * STOP / END [PROGRAM]
"""
import re

from . import astnodes as A


TOKEN_SPEC = [
    ("COMMENT_C", r"^[Cc*][^\n]*"),
    ("COMMENT_B", r"![^\n]*"),
    ("WS",        r"[ \t\r\n]+"),
    ("NUM",       r"\d+"),
    ("IDENT",     r"[A-Za-z][A-Za-z0-9_]*"),
    ("PUNCT",     r"[(),=+\-*/]"),
]
_TOKEN_RE = re.compile(
    "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC),
    re.MULTILINE)


KEYWORDS = {
    "PROGRAM", "END", "IMPLICIT", "NONE",
    "INTEGER", "REAL",
    "WRITE", "READ", "STOP",
}


def tokenize(text):
    tokens = []
    pos = 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if not m:
            raise SyntaxError(f"Ungueltiges Zeichen bei Pos {pos}: "
                              f"{text[pos:pos+20]!r}")
        typ, val = m.lastgroup, m.group()
        if typ in ("WS", "COMMENT_C", "COMMENT_B"):
            pass
        elif typ == "IDENT":
            up = val.upper()
            if up in KEYWORDS:
                tokens.append(("KW", up))
            else:
                tokens.append(("IDENT", val.lower()))
        elif typ == "NUM":
            tokens.append(("NUM", int(val)))
        else:
            tokens.append((typ, val))
        pos = m.end()
    tokens.append(("EOF", None))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _peek(self, off=0):
        return self.tokens[self.pos + off]

    def _eat(self, typ=None, val=None):
        tok = self.tokens[self.pos]
        if typ and tok[0] != typ:
            raise SyntaxError(f"Erwartet {typ}, gefunden {tok}")
        if val is not None and tok[1] != val:
            raise SyntaxError(f"Erwartet {val!r}, gefunden {tok[1]!r}")
        self.pos += 1
        return tok

    def _accept(self, typ, val=None):
        tok = self.tokens[self.pos]
        if tok[0] != typ:
            return None
        if val is not None and tok[1] != val:
            return None
        self.pos += 1
        return tok

    def parse_program(self):
        prog = A.Program(source_language="FORTRAN")

        self._eat("KW", "PROGRAM")
        prog.program_name = self._eat("IDENT")[1]

        if self._accept("KW", "IMPLICIT"):
            self._eat("KW", "NONE")

        while self._peek()[0] == "KW" and self._peek()[1] in ("INTEGER", "REAL"):
            self._eat()
            self._eat("IDENT")
            while self._accept("PUNCT", ","):
                self._eat("IDENT")

        while True:
            tok = self._peek()
            if tok[0] == "KW" and tok[1] in ("STOP", "END"):
                break
            stmt = self.parse_statement()
            if stmt is not None:
                prog.statements.append(stmt)

        self._accept("KW", "STOP")
        self._eat("KW", "END")
        self._accept("KW", "PROGRAM")
        self._eat("EOF")
        return prog

    def parse_statement(self):
        tok = self._peek()

        if tok[0] == "KW" and tok[1] == "WRITE":
            self._eat()
            self._eat("PUNCT", "(")
            while not self._accept("PUNCT", ")"):
                self._eat()
            expr = self.parse_expr()
            return A.Output(expr)

        if tok[0] == "IDENT":
            name = self._eat()[1]
            self._eat("PUNCT", "=")
            expr = self.parse_expr()
            return A.Assign(name, expr)

        raise SyntaxError(f"Unerwartetes FORTRAN-Statement: {tok}")

    def parse_expr(self):
        node = self.parse_term()
        while True:
            if self._accept("PUNCT", "+"):
                node = A.BinOp("+", node, self.parse_term())
            elif self._accept("PUNCT", "-"):
                node = A.BinOp("-", node, self.parse_term())
            else:
                return node

    def parse_term(self):
        tok = self._peek()
        if tok[0] == "NUM":
            self._eat()
            return A.Num(tok[1])
        if tok[0] == "IDENT":
            self._eat()
            return A.Var(tok[1])
        if tok[0] == "PUNCT" and tok[1] == "(":
            self._eat()
            e = self.parse_expr()
            self._eat("PUNCT", ")")
            return e
        raise SyntaxError(f"Ungueltiger FORTRAN-Term: {tok}")


def parse(source):
    return Parser(tokenize(source)).parse_program()