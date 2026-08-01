"""cpu_sim.compiler.compile -- Kommandozeilen-Frontend.

Aufruf:
    python -m src.compile <quelldatei>              # -> stdout
    python -m src.compile <quelldatei> -o <asm>     # -> Datei
    python -m src.compile <quelldatei> --ast        # zeige AST
    python -m src.compile <quelldatei> --run        # kompilieren + simulieren

Erkannte Endungen:
    .c        -> C-Frontend
    .f, .f77  -> FORTRAN-Frontend
    .cob      -> COBOL-Frontend
    .lisp, .lsp -> LISP-Frontend
"""
import os
import sys

from . import astnodes as A
from . import codegen


def frontend_for(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".c":
        from . import frontend_c
        return frontend_c, "C"
    if ext in (".f", ".f77", ".for"):
        from . import frontend_fortran
        return frontend_fortran, "FORTRAN"
    if ext == ".cob":
        from . import frontend_cobol
        return frontend_cobol, "COBOL"
    if ext in (".lisp", ".lsp", ".el"):
        from . import frontend_lisp
        return frontend_lisp, "LISP"
    raise ValueError(f"Unbekannte Endung: {ext} (fuer {path})")


def compile_source(source, language):
    if language == "C":
        from . import frontend_c as fe
    elif language == "FORTRAN":
        from . import frontend_fortran as fe
    elif language == "COBOL":
        from . import frontend_cobol as fe
    elif language == "LISP":
        from . import frontend_lisp as fe
    else:
        raise ValueError(f"Unbekannte Sprache: {language}")
    ast = fe.parse(source)
    return codegen.compile_ast(ast), ast


def compile_file(path):
    fe, lang = frontend_for(path)
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    ast = fe.parse(source)
    return codegen.compile_ast(ast), ast, lang


def _print_banner(lang, ast):
    print(f"[cpu-cc] Sprache={lang}", file=sys.stderr)
    if ast.program_name:
        print(f"[cpu-cc]   program-name = {ast.program_name}", file=sys.stderr)
    if ast.author:
        print(f"[cpu-cc]   author       = {ast.author}", file=sys.stderr)


def main(argv):
    args = argv[1:]
    if not args:
        print(__doc__)
        return 1

    src_path = None
    out_path = None
    show_ast = False
    run_after = False

    i = 0
    while i < len(args):
        a = args[i]
        if a == "-o" and i + 1 < len(args):
            out_path = args[i + 1]
            i += 2
        elif a == "--ast":
            show_ast = True
            i += 1
        elif a == "--run":
            run_after = True
            i += 1
        elif a.startswith("-"):
            print(f"Unbekannte Option: {a}", file=sys.stderr)
            return 2
        else:
            src_path = a
            i += 1

    if not src_path:
        print("Keine Quelldatei angegeben.", file=sys.stderr)
        return 2

    asm_text, ast, lang = compile_file(src_path)
    _print_banner(lang, ast)

    if show_ast:
        print(A.pp(ast))
        return 0

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(asm_text)
        print(f"[cpu-cc] geschrieben: {out_path}", file=sys.stderr)
    else:
        print(asm_text)

    if run_after:
        _simulate(asm_text)

    return 0


def _simulate(asm_text):
    # Compiler/src -> ../../02_OS/src  (Teil1_Grundlagen/02_OS/src)
    here = os.path.dirname(os.path.abspath(__file__))
    os_src = os.path.abspath(os.path.join(here, "..", "..",
                                          "02_OS", "src"))
    sys.path.insert(0, os_src)
    from cpu_sim import core, asm as cpuasm, config_two_reg

    cfg = config_two_reg.build_cpu_config()
    valid = set(cfg["microcode"].keys())
    prog = cpuasm.parse_asm(asm_text, valid)

    cpu = core.CPU(cfg, prog)
    for _ in range(500):
        if cpu.halted:
            break
        cpu.tick()

    print(f"[sim] halted={cpu.halted}  ticks={cpu.tick_counter}",
          file=sys.stderr)
    print(f"[sim] OUT = {cpu.out_reg.value:X}", file=sys.stderr)
    print(f"[sim] RAM[0..3] = "
          f"{[f'{cpu.ram.cells[i]:X}' for i in range(4)]}",
          file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main(sys.argv))