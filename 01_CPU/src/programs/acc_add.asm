; Akku-CPU: (3 + 4) - 1 = 6
; Speichert Ergebnis in RAM[5], laedt es zurueck, gibt an OUT.
;
; Die Akku-CPU hat kein TMP-Register. Der zweite Operand fuer
; ALU-Befehle kommt direkt aus dem Instruction Register - das
; heisst, "ADD n" addiert die Konstante n direkt zu ACC.

LDI 3        ; ACC ← 3
ADD 4        ; ACC ← ACC + 4  = 7      (Operand kommt aus IR)
SUB 1        ; ACC ← ACC - 1  = 6
STA 5        ; RAM[5] ← ACC
LDI 0        ; ACC ← 0        (Reset, um LDA sichtbar zu machen)
LDA 5        ; ACC ← RAM[5]   = 6
OUT          ; OUT-Register ← ACC
HLT