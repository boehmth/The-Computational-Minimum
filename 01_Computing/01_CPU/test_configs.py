"""Selbst-Test: beide CPU-Configs laufen headless durch."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cpu_sim import (core, asm, runner,
                     config_acc, config_minimal, config_two_reg)


def test(mod, expected):
    cfg = mod.build_cpu_config()
    valid = set(cfg["microcode"].keys())
    prog = asm.parse_asm(cfg["default_program"], valid)
    cpu = core.CPU(cfg, prog)
    runner.run_headless(cpu, max_ticks=500)
    ok = (cpu.halted and
          cpu.out_reg.value == expected["OUT"] and
          all(cpu.ram.cells[i] == v for i, v in expected["RAM"].items()))
    reg_name = "AX" if cfg.get("acc").name == "AX" else "ACC"
    print(f"{mod.__name__}: ticks={cpu.tick_counter} "
          f"halted={cpu.halted} {reg_name}={cpu.acc.value:X} "
          f"OUT={cpu.out_reg.value:X} "
          f"RAM=" + " ".join(f"{i:X}:{v:X}"
                              for i, v in enumerate(cpu.ram.cells) if v)
          + ("   OK" if ok else "   FAIL"))
    return ok


# Akku-CPU: (3+4)-1 = 6, in RAM[5] und in OUT
ok1 = test(config_acc,     {"OUT": 6, "RAM": {5: 6}})
# Minimal-CPU: zaehlt bis 5, Ergebnis in RAM[0] und OUT
ok2 = test(config_minimal, {"OUT": 5, "RAM": {0: 5}})
# Zwei-Register-CPU: (3+4)-1 = 6, in RAM[5] und in OUT
ok3 = test(config_two_reg, {"OUT": 6, "RAM": {5: 6}})

print()
print("All OK" if (ok1 and ok2 and ok3) else "FAIL")
sys.exit(0 if (ok1 and ok2 and ok3) else 1)
