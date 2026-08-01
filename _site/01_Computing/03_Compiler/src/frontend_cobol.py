"""Frontend fuer COBOL-artige Syntax (1959er-Stil).

Beispiel:

    IDENTIFICATION DIVISION.
    PROGRAM-ID. ARITHMETIK.
    AUTHOR. STUDIERENDE.
    DATA DIVISION.
    WORKING-STORAGE SECTION.
    01 X PIC 9.
    01 Y PIC 9.
    01 Z PIC 9.
    PROCEDURE DIVISION.
    BEGIN-PROGRAM.
        COMPUTE X = 3.
        COMPUTE Y = 4.
        ADD Y TO X GIVING Z.
        SUBTRACT 1 FROM Z.
        DISPLAY Z.
        STOP RUN.
    END-PROGRAM.

Statement-Semantik:
    COMPUTE x = 3          -> x = 3
    ADD y TO x GIVING z    -> z = x + y
    SUBTRACT 1 FROM z      -> z = z - 1
    DISPLAY z              -> print(z)
"""
import re

from . import astnodes as A


TOKEN_SPEC = [
    ("WS",      r"[ \t\r\n]+"),
    ("COMMENT", r"\*>[^\n]*"),
    ("NUM",     r"\d+"),
    ("IDENT",   r"[A-Za-z][A-Za-z0-9_-]*"),
    ("DOT",     r"\."),
    ("EQ",      r"="),
    ("OP",      r"[+\-]"),
]
_TOKEN_RE = re.compile(
    "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))


KEYWORDS = {
    "IDENTIFICATION", "DIVISION", "ENVIRONMENT", "DATA", "PROCEDURE",
    "PROGRAM-ID", "AUTHOR", "DATE-WRITTEN",
    "WORKING-STORAGE", "SECTION",
    "COMPUTE", "ADD", "SUBTRACT", "TO", "FROM", "GIVING",
    "DISPLAY", "STOP", "RUN",
    "PIC",
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
        if typ in ("WS", "COMMENT"):
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
        prog = A.Program(source_language="COBOL")

        self._eat("KW", "IDENTIFICATION")
        self._eat("KW", "DIVISION")
        self._eat("DOT")

        self._eat("KW", "PROGRAM-ID")
        self._eat("DOT")
        prog.program_name = self._eat("IDENT")[1]
        self._eat("DOT")

        if self._accept("KW", "AUTHOR"):
            self._eat("DOT")
            author_words = []
            while not self._accept("DOT"):
                tok = self._eat()
                author_words.append(str(tok[1]))
            prog.author = " ".join(author_words)

        if self._accept("KW", "DATE-WRITTEN"):
            self._eat("DOT")
            while not self._accept("DOT"):
                self._eat()

        if self._accept("KW", "DATA"):
            self._eat("KW", "DIVISION")
            self._eat("DOT")

            self._eat("KW", "WORKING-STORAGE")
            self._eat("KW", "SECTION")
            self._eat("DOT")

            while self._peek()[0] == "NUM":
                self._eat("NUM")
                self._eat("IDENT")
                while not self._accept("DOT"):
                    self._eat()

        self._eat("KW", "PROCEDURE")
        self._eat("KW", "DIVISION")
        self._eat("DOT")

        while (self._peek()[0] == "IDENT"
               and self._peek(1)[0] == "DOT"):
            self._eat("IDENT")
            self._eat("DOT")

        while True:
            tok = self._peek()
            if tok[0] == "KW" and tok[1] == "STOP":
                break
            if tok[0] == "EOF":
                break
            stmt = self.parse_statement()
            if stmt is not None:
                prog.statements.append(stmt)

        self._accept("KW", "STOP")
        self._accept("KW", "RUN")
        self._accept("DOT")

        while self._peek()[0] != "EOF":
            self._eat()
        self._eat("EOF")

        return prog

    def parse_statement(self):
        tok = self._peek()

        if tok[0] == "KW" and tok[1] == "COMPUTE":
            self._eat()
            name = self._eat("IDENT")[1]
            self._eat("EQ")
            expr = self.parse_expr()
            self._eat("DOT")
            return A.Assign(name, expr)

        if tok[0] == "KW" and tok[1] == "ADD":
            self._eat()
            src = self.parse_atom()
            self._eat("KW", "TO")
            dst = self._eat("IDENT")[1]
            if self._accept("KW", "GIVING"):
                result = self._eat("IDENT")[1]
                self._eat("DOT")
                return A.Assign(result, A.BinOp("+", A.Var(dst), src))
            self._eat("DOT")
            return A.Assign(dst, A.BinOp("+", A.Var(dst), src))

        if tok[0] == "KW" and tok[1] == "SUBTRACT":
            self._eat()
            src = self.parse_atom()
            self._eat("KW", "FROM")
            dst = self._eat("IDENT")[1]
            if self._accept("KW", "GIVING"):
                result = self._eat("IDENT")[1]
                self._eat("DOT")
                return A.Assign(result, A.BinOp("-", A.Var(dst), src))
            self._eat("DOT")
            return A.Assign(dst, A.BinOp("-", A.Var(dst), src))

        if tok[0] == "KW" and tok[1] == "DISPLAY":
            self._eat()
            expr = self.parse_expr()
            self._eat("DOT")
            return A.Output(expr)

        raise SyntaxError(f"Unerwartetes COBOL-Statement: {tok}")

    def parse_expr(self):
        node = self.parse_atom()
        while True:
            if self._accept("OP", "+"):
                node = A.BinOp("+", node, self.parse_atom())
            elif self._accept("OP", "-"):
                node = A.BinOp("-", node, self.parse_atom())
            else:
                return node

    def parse_atom(self):
        tok = self._peek()
        if tok[0] == "NUM":
            self._eat()
            return A.Num(tok[1])
        if tok[0] == "IDENT":
            self._eat()
            return A.Var(tok[1])
        raise SyntaxError(f"Ungueltiges COBOL-Atom: {tok}")


def parse(source):
    return Parser(tokenize(source)).parse_program()