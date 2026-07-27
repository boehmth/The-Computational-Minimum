; job_evil -- ein "boeser" Job, der den OS-State ueberschreibt.
;
; Zeigt: in unserem Batch-OS gibt es KEINEN Speicherschutz. RAM[0]
; gehoert per Konvention dem OS (dort steht der last_program_index),
; aber technisch kann jeder Job dort hineinschreiben. Wenn wir das
; tun, bekommen wir eine Manipulation des Schedulers -- der OS-Zaehler
; springt beim naechsten Durchlauf zu einem anderen Wert als erwartet.
;
; Konkret: dieses Programm schreibt 7 in RAM[0]. Beim naechsten
; OS-Durchlauf ist last_index=7, next_index=8 -- das OS springt also
; direkt zu Slot 8 (leer -> sofort zurueck), 9 (leer), ..., statt in
; der Reihenfolge weiterzumachen.
;
; Das ist realistisch: in DOS < 5.0 oder CP/M konnte jedes User-Programm
; den Kernel-State bearbeiten. Fehler dieser Art waren die Regel.
;
; Was NICHT passiert (im Batch-OS): der Rechner crasht. Das OS ist
; robust genug -- der Wrap ueber 15 -> 1 rettet uns davor, dass RAM[0]
; jemals ein Wert steht, der zu BP=0 fuehrt. Selbst boese User bleiben
; im User-Space, wenn auch in willkuerlicher Reihenfolge.

LDI  7      ; AX := 7
STA  0      ; RAM[0] := 7      <-- HIER ist der Uebergriff!
            ;                       (per Konvention verboten)
OUT         ; OUT := 7          (nur damit man sieht, dass wir was tun)
HLT         ; -> zurueck ans OS -- das aber jetzt "verwirrt" ist