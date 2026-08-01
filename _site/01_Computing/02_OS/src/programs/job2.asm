; job2 -- Schleife: zaehlt in RAM[2] hoch bis 4, dann HLT.
;
; Zeigt, dass ein Job auch interne Kontrollfluesse (JMP, JZ) haben
; darf. Am Ende steht HLT -> Kontrolle zurueck ans OS.

LDI 0       ; 0: AX := 0
STA 2       ; 1: RAM[2] := 0            (Zaehler initialisieren)

            ;    -- Schleifenkopf bei Adresse 2 --
LDA 2       ; 2: AX := RAM[2]
LDB 1       ; 3: BX := 1
ADD         ; 4: AX := AX + 1
STA 2       ; 5: RAM[2] := AX
OUT         ; 6: OUT := AX

LDB 4       ; 7: BX := 4
SUB         ; 8: AX := AX - 4           (0 wenn Zaehler == 4)
JZ  B       ; 9: falls 0 -> Sprung nach B (HLT)
JMP 2       ; A: sonst zurueck zum Schleifenkopf
HLT         ; B: fertig -> zurueck ans OS