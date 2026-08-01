; ============================================================
;  Perceptron  --  ein Neuron in 16 Instruktionen
; ============================================================
;
; Berechnet die klassische Perceptron-Formel:
;
;     y = 1  if  (w1*x1 + w2*x2 + b) > 0
;     y = 0  sonst
;
; Alle Werte sind 4-Bit-Zweierkomplement:
;    Bit-Muster  Unsigned  Signed (2K)
;    0000..0111     0..7     0..7
;    1000..1111     8..15   -8..-1
;
; Das obere Bit von AX ist damit das Vorzeichen. Der JN-Opcode
; ("Jump if Negative") testet dieses Bit direkt.
;
; RAM-Layout:
;    RAM[0] = x1       Eingang 1
;    RAM[1] = x2       Eingang 2
;    RAM[2] = w1       Gewicht 1 (2K)
;    RAM[3] = w2       Gewicht 2 (2K)
;    RAM[4] = b        Bias    (2K)
;    RAM[5] = partial  Zwischenergebnis x2*w2 + b
;
; Diese Werte muessen VOR dem Start ins RAM geschrieben werden.
; Der Runner (test_perceptron.py bzw. run_perceptron.py) setzt sie
; z.B. auf x1=1, x2=1, w1=1, w2=1, b=-1  (AND-Perceptron).
;
; Programmablauf (linear + zwei Spruenge am Ende):
;    Adr  Instr   Kommentar
;     0   LDA 1   AX := x2
;     1   LDBM 3  BX := w2
;     2   MUL     AX := x2 * w2
;     3   LDBM 4  BX := b
;     4   ADD     AX := x2*w2 + b
;     5   STA 5   partial := AX          (merken fuer spaeter)
;     6   LDA 0   AX := x1
;     7   LDBM 2  BX := w1
;     8   MUL     AX := x1 * w1
;     9   LDBM 5  BX := partial (= x2*w2 + b)
;     A   ADD     AX := x1*w1 + x2*w2 + b   -- die volle Perceptron-Summe
;     B   JN  E   wenn AX<0 (also Summe negativ) springe zu E: setze 0
;     C   LDI 1   AX := 1                (positiver Fall, sum>=0 -> feuert)
;     D   JMP F   ueberspringe das LDI 0
;     E   LDI 0   AX := 0                (negativer Fall)
;     F   OUT     OUT := y               (letzte Instruktion im Slot)
;
; Kein HLT: das Programm belegt genau die 16 Instruktionen eines
; Batch-OS-Slots. Nach Adresse F folgt der leere Slot-Rand
; (Opcode 0 = HLT), das Batch-OS bekommt die Kontrolle zurueck.

LDA 1        ; 0: AX := x2
LDBM 3       ; 1: BX := w2
MUL          ; 2: AX := x2*w2
LDBM 4       ; 3: BX := b
ADD          ; 4: AX := x2*w2 + b
STA 5        ; 5: partial := AX
LDA 0        ; 6: AX := x1
LDBM 2       ; 7: BX := w1
MUL          ; 8: AX := x1*w1
LDBM 5       ; 9: BX := partial
ADD          ; A: AX := x1*w1 + x2*w2 + b
JN  E        ; B: if AX<0 -> E
LDI 1        ; C: AX := 1  (positiver Fall)
JMP F        ; D: ueberspringe 0-Zweig
LDI 0        ; E: AX := 0  (negativer Fall)
OUT          ; F: OUT := y