"""Frontend fuer C-artige Syntax.

Erlaubte Programme sind winzig aber typisch C:

    #include <stdio.h>

    int main(void) {
        int x = 3;
        int y = 4;
        int z = (x + y) - 1;
        printf("%d\n", z);
        return 0;
    }

Grammatik (rekursiver Abstieg):

    program    := preprocessor* function
    function   := 'int' 'main' '(' 'void'? ')' block
    block      := '{' statement* '}'
    statement  := decl | assign | printf | return
    decl       := 'int' IDENT '=' expr ';'
    assign     := IDENT '=' expr ';'
    printf     := 'printf' '(' STRING ',' expr ')' ';'
    return     := 'return' expr ';'
    expr       := term (('+' | '-') term)*
    term       := NUM | IDENT | '(' expr ')'

Wir ignorieren das `#include`-Praeprozessor-Zeug (rein syntaktisch)
und den `return` von main. `printf(..., x)` -> `Output(x)`.
"""
import re

from . import astnodes as A


TOKEN_SPEC = [
    ("WS",       r"[ \t\r\n]+"),
    ("COMMENT1", r"//[^\n]*"),
    ("COMMENT2", r"/\*.*?\*/"),
    ("STRING",   r'"[^"]*"'),
    ("NUM",      r"0x[0-9A-Fa-f]+|\d+"),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    ("PUNCT",    r"[{}();,#<>.]|=|\+|-|\*"),
]
_TOKEN_RE = re.compile(
    "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC),
    re.DOTALL)


KEYWORDS = {"int", "void", "main", "printf", "return", "include"}


def tokenize(text):
    tokens = []
    pos = 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if not m:
            raise SyntaxError(f"Ungueltiges Zeichen bei Pos {pos}: "
                              f"{text[pos:pos+20]!r}")
        typ, val = m.lastgroup, m.group()
        if typ in ("WS", "COMMENT1", "COMMENT2"):
            pass
        elif typ == "IDENT" and val in KEYWORDS:
            tokens.append(("KW", val))
        elif typ == "STRING":
            tokens.append(("STRING", val[1:-1]))
        elif typ == "NUM":
            v = int(val, 16) if val.lower().startswith("0x") else int(val)
            tokens.append(("NUM", v))
        else:
            tokens.append((typ, val))
        pos = m.end()
    tokens.append(("EOF", None))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _peek(self, offset=0):
        return self.tokens[self.pos + offset]

    def _eat(self, expected_type=None, expected_val=None):
        tok = self.tokens[self.pos]
        if expected_type and tok[0] != expected_type:
            raise SyntaxError(
                f"Erwartet {expected_type} bei Token {self.pos}, "
                f"gefunden {tok}")
        if expected_val is not None and tok[1] != expected_val:
            raise SyntaxError(
                f"Erwartet {expected_val!r} bei Token {self.pos}, "
                f"gefunden {tok[1]!r}")
        self.pos += 1
        return tok

    def _accept(self, type_, val=None):
        tok = self.tokens[self.pos]
        if tok[0] != type_:
            return None
        if val is not None and tok[1] != val:
            return None
        self.pos += 1
        return tok

    def parse_program(self):
        prog = A.Program(source_language="C")

        while self._accept("PUNCT", "#"):
            self._eat("KW", "include")
            if self._accept("PUNCT", "<"):
                self._eat("IDENT")
                self._eat("PUNCT", ".")
                self._eat("IDENT")
                self._eat("PUNCT", ">")
            else:
                self._eat("STRING")

        self._eat("KW", "int")
        self._eat("KW", "main")
        self._eat("PUNCT", "(")
        self._accept("KW", "void")
        self._eat("PUNCT", ")")
        self._eat("PUNCT", "{")

        while not self._accept("PUNCT", "}"):
            stmt = self.parse_statement()
            if stmt is not None:
                prog.statements.append(stmt)

        self._eat("EOF")
        prog.program_name = "main"
        return prog

    def parse_statement(self):
        tok_typ, tok_val = self._peek()

        if tok_typ == "KW" and tok_val == "int":
            self._eat()
            name = self._eat("IDENT")[1]
            self._eat("PUNCT", "=")
            expr = self.parse_expr()
            self._eat("PUNCT", ";")
            return A.Assign(name, expr)

        if tok_typ == "KW" and tok_val == "printf":
            self._eat()
            self._eat("PUNCT", "(")
            self._eat("STRING")
            self._eat("PUNCT", ",")
            expr = self.parse_expr()
            self._eat("PUNCT", ")")
            self._eat("PUNCT", ";")
            return A.Output(expr)

        if tok_typ == "KW" and tok_val == "return":
            self._eat()
            self.parse_expr()
            self._eat("PUNCT", ";")
            return None

        if tok_typ == "IDENT":
            name = self._eat()[1]
            self._eat("PUNCT", "=")
            expr = self.parse_expr()
            self._eat("PUNCT", ";")
            return A.Assign(name, expr)

        raise SyntaxError(f"Unerwartetes Statement bei Token {self.pos}: "
                          f"{self._peek()}")

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
        raise SyntaxError(f"Ungueltiger Term: {tok}")


def parse(source):
    return Parser(tokenize(source)).parse_program()