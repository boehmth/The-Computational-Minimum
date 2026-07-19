; ============================================================
;  OS  --  Batch-Betriebssystem in 16 Instruktionen (Slot BP=0)
; ============================================================
;
; Kontrakt mit der CPU:
;   * Das OS liegt bei BP=0. Beim Boot ist PC=0, BP=0 -> OS laeuft.
;   * User-Programme liegen bei BP=1..15. Ein User-Programm gibt die
;     Kontrolle mit HLT zurueck; die CPU setzt dann automatisch
;     BP:=0, PC:=0 -- das OS erhaelt die Kontrolle zurueck.
;   * Leerer Programmspeicher (Opcode 0 = HLT) fuehrt sofort ins OS.
;
; State im RAM (ungeschuetzt, gemeinsam mit User-Programmen!):
;   RAM[0] = "last_program_index" (0 beim Boot, wird pro OS-Run
;            um 1 hochgezaehlt und identifiziert den naechsten Job).
;
; Ablauf pro OS-Durchgang:
;   1. Naechsten Job-Index berechnen: next = RAM[0] + 1.
;   2. Wenn next == 0 (4-Bit-Overflow, also 15+1=0): auf 1 wrappen,
;      damit BP=0 (=OS-Slot) nicht als Job aufgerufen wird.
;   3. RAM[0] := next (persistieren).
;   4. BX := next (SETBP nimmt seinen Wert aus BX).
;   5. AX := 0 (Register sauber fuer User -- optional; BX ist noch next,
;      das User-Programm sieht das, was etwas verschwenderisch, aber
;      ehrlich ist).
;   6. SETBP: BP := BX, PC := 0. Kontrolle geht an User-Programm.
;
; Wenn ein User-Programm HLT macht, geht die CPU automatisch zurueck
; auf BP=0, PC=0 und das OS laeuft von vorne. So wandert der Index
; monoton durch alle 15 User-Slots (mit Wrap ueber die 0).
;
; Groesse: 10 Instruktionen von 16 verfuegbaren.
; -----------------------------------------------------------

LDA   0     ; 0: AX := RAM[0]        (last_index)
LDB   1     ; 1: BX := 1
ADD         ; 2: AX := AX + BX        (next_index = last+1)
JZ    5     ; 3: falls Overflow (AX==0) -> Reset-Zweig bei Adresse 5
JMP   7     ; 4: sonst weiter bei Adresse 7 (STA)
LDI   1     ; 5: Reset: AX := 1       (skip OS-Slot beim Wrap)
NOP         ; 6: fill (fallthrough zu 7)
STA   0     ; 7: RAM[0] := AX         (persistiere next_index)
MOV         ; 8: BX := AX             (SETBP-Argument nach BX)
SETBP       ; 9: BP := BX, PC := 0    (User-Prog starten -- OS-Ende)