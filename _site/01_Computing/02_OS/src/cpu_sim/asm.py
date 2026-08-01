"""cpu_sim.asm -- kleiner Assembler.

Syntax:
    MNEMONIC [OPERAND]  ; kommentar
    MNEMONIC [OPERAND]  # kommentar

Operanden:
    - dezimal:  3
    - hex:      0xF   oder $F
    - binaer:   0b1010

Der gueltige Opcode-Satz kommt aus einer CPU-Config
(dict mit den Opcodes als Keys, z.B. dem MICROCODE-Dict).
"""


def parse_operand(token):
    """Erlaubt: 0xN, $N, 0bNNNN, sonst dezimal.
    Zusaetzlich: einzelne Hex-Ziffern (A-F) werden als hex akzeptiert,
    damit man einfach 'JZ E' schreiben kann. In diesem Modell haben
    Operanden ohnehin nur 4 Bit (0..F), Verwechslung mit Zahlen ist
    also unwahrscheinlich."""
    token = token.strip()
    if token.startswith("0x") or token.startswith("0X"):
        return int(token, 16)
    if token.startswith("$"):
        return int(token[1:], 16)
    if token.startswith("0b") or token.startswith("0B"):
        return int(token, 2)
    # Einzelne Hex-Ziffer (A..F oder a..f) als hex akzeptieren
    if len(token) == 1 and token.upper() in "ABCDEF":
        return int(token, 16)
    return int(token, 10)


def parse_asm(text, valid_opcodes):
    """Parst Assembler-Text und gibt Liste (opcode, operand) zurueck.

    valid_opcodes: Menge/Container erlaubter Opcode-Strings.
    """
    program = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        for cc in (";", "#"):
            i = raw.find(cc)
            if i >= 0:
                raw = raw[:i]
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        opcode = parts[0].upper()
        if opcode not in valid_opcodes:
            raise ValueError(
                f"Zeile {lineno}: unbekannter Opcode '{opcode}'"
                f" (erlaubt: {sorted(valid_opcodes)})")
        operand = parse_operand(parts[1]) if len(parts) > 1 else 0
        if not (0 <= operand <= 0xF):
            raise ValueError(
                f"Zeile {lineno}: Operand {operand} nicht in 4-Bit-Bereich 0..F")
        program.append((opcode, operand))
    return program


def load_program(path, fallback_text, valid_opcodes):
    """Laedt Programm aus Datei, faellt auf fallback_text zurueck.
    Gibt (program, source) zurueck."""
    import os
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return parse_asm(f.read(), valid_opcodes), path
    return parse_asm(fallback_text, valid_opcodes), "(inline default)"