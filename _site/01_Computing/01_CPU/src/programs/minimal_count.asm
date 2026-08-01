; Minimal-CPU: zeigt Zaehlschleife mit INC + JZ + JMP.
;
; Zaehlt ACC von 0 hoch bis 5 und legt jeden Zwischenwert in OUT.
; Loop-Counter (RAM[1]) startet bei -5 (2er-Komplement = 0xB)
; und wird jeden Durchgang mit INC in Richtung 0 hochgezaehlt.
;
; Adressen sind hexadezimal (0..F). Zur Sicherheit hier explizit
; mit $-Prefix geschrieben.

LDI 0        ; 0:  ACC = 0  (Ergebnis)
STA 0        ; 1:  RAM[0] = 0
LDI 5        ; 2:  ACC = 5
NOT          ; 3:  ACC = ~5 = 0xA
INC          ; 4:  ACC = 0xB = -5 (2er-Komplement)
STA 1        ; 5:  RAM[1] = -5 (Counter)

; --- Schleifenkopf: Adresse 6 ---
LDA 0        ; 6:  ACC = RAM[0]
INC          ; 7:  ACC += 1
STA 0        ; 8:  RAM[0] = ACC
OUT          ; 9:  OUT   = ACC

LDA 1        ; A:  ACC = Counter
INC          ; B:  Counter += 1 (Richtung 0)
STA 1        ; C:  RAM[1] = ACC (aktualisiert)
JZ  $F       ; D:  wenn ACC=0 -> Ende bei Adresse F
JMP 6        ; E:  ... zurueck zum Schleifenkopf

HLT          ; F:  Endezeichen
