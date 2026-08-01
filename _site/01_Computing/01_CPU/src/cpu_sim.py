"""cpu_sim -- Runner fuer die 4-Bit-CPU-Simulation.

Aufruf:
    python cpu_sim.py [<config>] [<programm.asm>]

<config> ist eine der Kurzformen 'acc' / 'minimal' oder ein
Modulpfad wie 'cpu_sim.config_acc'. Default: acc.

<programm.asm> ist eine Assembler-Datei (siehe cpu_sim/asm.py).
Wird sie weggelassen, wird das DEFAULT_PROGRAM der Config benutzt.

Beispiele:
    python cpu_sim.py                                  # acc, default
    python cpu_sim.py acc     programs/acc_add.asm
    python cpu_sim.py minimal programs/minimal_count.asm
"""
import importlib
import sys

from cpu_sim import core, asm, runner


CONFIG_ALIASES = {
    # Akku-CPU: ein Register (ACC) + ALU-Operand aus IR
    "acc":       "cpu_sim.config_acc",
    "accu":      "cpu_sim.config_acc",
    "sap1":      "cpu_sim.config_acc",  # historisch: Malvinos SAP-1
    # Minimalist-CPU: nur ACC, ALU unaer (INC/NOT)
    "minimal":   "cpu_sim.config_minimal",
    "min":       "cpu_sim.config_minimal",
    # Zwei-Register-CPU: AX + BX, Register-Register-Ops
    "two_reg":   "cpu_sim.config_two_reg",
    "two-reg":   "cpu_sim.config_two_reg",
    "2reg":      "cpu_sim.config_two_reg",
    "axbx":      "cpu_sim.config_two_reg",
}


def resolve_config(name):
    modname = CONFIG_ALIASES.get(name, name)
    return importlib.import_module(modname)


def main(argv):
    args = argv[1:]

    # Argumente parsen (beide sind optional)
    config_name = "acc"
    asm_path = None
    if len(args) >= 1:
        # Falls Endet auf .asm, dann ist es ein Programm und Config bleibt default
        if args[0].endswith(".asm"):
            asm_path = args[0]
        else:
            config_name = args[0]
    if len(args) >= 2:
        asm_path = args[1]

    # Config laden -> CPU bauen
    config_mod = resolve_config(config_name)
    config = config_mod.build_cpu_config()

    # Programm laden
    valid_opcodes = set(config["microcode"].keys())
    program, source = asm.load_program(
        asm_path, config["default_program"], valid_opcodes)

    cpu = core.CPU(config, program)

    # Los!
    runner.run(cpu, source=source)


if __name__ == "__main__":
    # Auf Windows: UTF-8 fuer die Box-Zeichen erzwingen
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    main(sys.argv)