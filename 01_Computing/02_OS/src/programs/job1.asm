; job1 -- addiert 3 + 4, gibt 7 aus, speichert in RAM[1], HLT.
;
; Wichtig: dieses Programm laeuft in einem Slot bei BP>=1 (das OS
; sorgt dafuer). RAM ist NICHT segmentiert und wird mit dem OS
; geteilt -- RAM[0] gehoert dem OS, wir schreiben brav in RAM[1..].
;
; Nach HLT setzt die CPU automatisch BP:=0, PC:=0 und das OS bekommt
; die Kontrolle zurueck.

LDI  3      ; AX := 3
LDB  4      ; BX := 4
ADD         ; AX := 7
STA  1      ; RAM[1] := 7   (Ergebnis persistieren)
OUT         ; OUT := 7      (sichtbar am OUT-Register)
HLT         ; -> zurueck ans OS