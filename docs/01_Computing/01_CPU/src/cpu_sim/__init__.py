"""cpu_sim -- 4-bit CPU simulator framework.

Struktur:
    core.py          - Framework: Element, Bus, ControlUnit, Views
    asm.py           - Assembler
    runner.py        - Simulator-Loop und Layout
    config_*.py      - CPU-Konfigurationen (welche Elemente, welche
                       Mikrocodes)

Nutzung (siehe cpu_sim.py im Parent-Verzeichnis):
    from cpu_sim import core, asm, runner
    from cpu_sim.config_two_reg import build_cpu, MICROCODE, OPCODE_INFO
    ...
"""