; Prozess A: zaehlt in RAM[0] von 0 nach oben, dann YIELD, dann wieder.
; Laeuft in seinem eigenen Segment (SEG=1 wird vom OS gesetzt).
;
; RAM[0] ist logisch, physisch also SEG=1 -> RAM[0x10].

LDI 0         ; 0: AX = 0
STA 0         ; 1: RAM[0] = 0
              ; --- Schleife (Adresse 2) ---
LDA 0         ; 2: AX = RAM[0]
LDB 1         ; 3: BX = 1
ADD           ; 4: AX = AX + BX
STA 0         ; 5: RAM[0] = AX
OUT           ; 6: OUT = AX
YIELD         ; 7: gib Kontrolle ans OS
JMP 2         ; 8: zurueck zum Schleifenkopf