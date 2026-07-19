"""cpu_sim.mini_os -- ein winziges kooperatives Multitasking-OS.

Konzept:
  * Das OS haelt eine Prozess-Tabelle mit zwei Prozessen.
  * Jeder Prozess besitzt sein eigenes RAM-Segment (SEG=1 bzw. SEG=2).
  * SEG=0 ist das OS-eigene Segment. Dort speichert das OS die
    Prozess-Kontexte (PC, AX, BX, SEG) als 4 Zellen pro Prozess.
  * Bei jedem YIELD-Opcode setzt die CPU cpu.yielded=True. Das OS
    fragt das nach jedem Takt ab und macht dann einen Context-Switch:
      1) aktuellen Kontext (PC, AX, BX, SEG) im OS-Segment sichern
      2) naechsten Prozess auswaehlen (Round-Robin)
      3) dessen Kontext laden
      4) dessen Programm-Code in cpu.program eintragen (Harvard-Fake:
         weil unsere Program-Liste ausserhalb des RAM liegt, muss das
         OS die passende Liste der CPU zuweisen — auf echter Hardware
         waere das Programm einfach an einer anderen physischen Adresse)

Speicher-Layout im OS-Segment (SEG=0), 4 Zellen pro Prozess:
    OS[0] = Prozess-0 PC
    OS[1] = Prozess-0 AX
    OS[2] = Prozess-0 BX
    OS[3] = Prozess-0 SEG (immer 1)
    OS[4] = Prozess-1 PC
    OS[5] = Prozess-1 AX
    OS[6] = Prozess-1 BX
    OS[7] = Prozess-1 SEG (immer 2)
    OS[F] = aktueller Prozess-Index (0 oder 1)   ← zur Anzeige
"""


class Process:
    def __init__(self, pid, name, program, seg):
        self.pid = pid
        self.name = name
        self.program = program
        self.seg = seg          # Datensegment dieses Prozesses
        self.halted = False
        # Statistik
        self.ticks_used = 0
        self.yields = 0


class MiniOS:
    """Kooperatives Multitasking-OS fuer 2 Prozesse."""

    # Layout im OS-Segment (SEG=0)
    OFFSET_PC   = 0
    OFFSET_AX   = 1
    OFFSET_BX   = 2
    OFFSET_SEG  = 3
    SLOT_SIZE   = 4              # 4 Zellen pro Prozess
    OFFSET_CURRENT = 0xF         # letzte Zelle: aktueller Prozess

    def __init__(self, cpu, programs):
        """programs: [(name, program_list), ...]  (2 Eintraege)"""
        if len(programs) != 2:
            raise ValueError("MiniOS erwartet genau 2 Programme")
        if cpu.seg is None:
            raise ValueError("Die CPU-Config muss ein SEG-Register haben")

        self.cpu = cpu
        self.processes = [
            Process(0, programs[0][0], programs[0][1], seg=1),
            Process(1, programs[1][0], programs[1][1], seg=2),
        ]
        self.current = 0

        # OS-Segment initialisieren: alle Kontexte auf 0, SEG passend
        for p in self.processes:
            base = p.pid * self.SLOT_SIZE
            self.cpu.ram.cells[base + self.OFFSET_PC]  = 0
            self.cpu.ram.cells[base + self.OFFSET_AX]  = 0
            self.cpu.ram.cells[base + self.OFFSET_BX]  = 0
            self.cpu.ram.cells[base + self.OFFSET_SEG] = p.seg
        self.cpu.ram.cells[self.OFFSET_CURRENT] = 0

        # Den ersten Prozess laden
        self._load_context(self.current)

    # ---------- privilegierter Hardware-Zugriff -------------
    # Diese beiden Methoden umgehen bewusst den normalen Bus-Zyklus.
    # Das ist die Simulations-Analogie zu "Kernel-Ring 0": das OS
    # kann Register direkt schreiben, User-Code nicht.

    def _save_context(self, pid):
        """Aktuellen CPU-Zustand als Kontext von pid speichern."""
        base = pid * self.SLOT_SIZE
        self.cpu.ram.cells[base + self.OFFSET_PC]  = self.cpu.pc.value
        self.cpu.ram.cells[base + self.OFFSET_AX]  = self.cpu.acc.value  # AX
        self.cpu.ram.cells[base + self.OFFSET_BX]  = self.cpu.tmp.value  # BX
        self.cpu.ram.cells[base + self.OFFSET_SEG] = self.cpu.seg.value

    def _load_context(self, pid):
        """Kontext von pid in die CPU-Register laden + Programm setzen."""
        base = pid * self.SLOT_SIZE
        proc = self.processes[pid]

        self.cpu.pc.value  = self.cpu.ram.cells[base + self.OFFSET_PC]
        self.cpu.acc.value = self.cpu.ram.cells[base + self.OFFSET_AX]
        self.cpu.tmp.value = self.cpu.ram.cells[base + self.OFFSET_BX]
        self.cpu.seg.value = self.cpu.ram.cells[base + self.OFFSET_SEG]

        # "Harvard-Fake": Programmspeicher des Prozesses laden.
        # Auf echter Hardware waeren alle Programme gleichzeitig im
        # Prog-ROM/RAM, an unterschiedlichen physischen Adressen. Hier
        # tauschen wir einfach die 'program'-Liste der CPU aus.
        self.cpu.program = proc.program

        # CU-Zustand zuruecksetzen (wir starten sauber mit FETCH)
        self.cpu.cu.step = 0
        self.cpu.cu.current_opcode = "NOP"
        self.cpu.cu.current_operand = 0

        self.cpu.yielded = False
        self.cpu.halted = False   # der Nachfolger darf laufen

        # Anzeige-Zelle im OS-Segment updaten
        self.cpu.ram.cells[self.OFFSET_CURRENT] = pid

    # ---------- Scheduler -----------------------------------
    def context_switch(self):
        """Von self.current zum naechsten nicht-halted Prozess wechseln."""
        # Aktuellen Kontext sichern
        self._save_context(self.current)
        self.processes[self.current].yields += 1

        # Naechsten Prozess suchen (Round-Robin, ueberspringt halted)
        n = len(self.processes)
        for _ in range(n):
            self.current = (self.current + 1) % n
            if not self.processes[self.current].halted:
                break
        self._load_context(self.current)

    def all_halted(self):
        return all(p.halted for p in self.processes)

    # ---------- Ein Tick + Scheduler --------------------
    def tick(self):
        """Ein CPU-Tick + evtl. Context-Switch danach."""
        if self.all_halted():
            return
        proc = self.processes[self.current]
        self.cpu.tick()
        proc.ticks_used += 1

        # Falls der Prozess in diesem Tick HLT gemacht hat: als halted markieren
        if self.cpu.halted:
            proc.halted = True
            if not self.all_halted():
                # Anderer Prozess soll weiterlaufen
                self.context_switch()
            return

        # Falls YIELD passiert ist: Context-Switch
        if self.cpu.yielded:
            self.context_switch()