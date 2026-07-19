; Zwei-Register-CPU: (3 + 4) - 1 = 6, mit echten Register-Register-Ops.
;
; Auf einer Akku-CPU wuerde man dafuer "ADD 4" schreiben - die Konstante
; kommt aus IR. Auf der Zwei-Register-CPU zeigt "ADD" hingegen keine
; Konstante mehr: es rechnet immer AX + BX. Daher muss man BX vorher
; passend fuellen (per LDB fuer Immediate, oder LDBM fuer RAM-Load).

LDI  3       ; AX ← 3
LDB  4       ; BX ← 4
ADD          ; AX ← AX + BX = 7    (Register-Register-Op)
LDB  1       ; BX ← 1
SUB          ; AX ← AX - BX = 6
STA  5       ; RAM[5] ← AX
LDI  0       ; AX ← 0
LDA  5       ; AX ← RAM[5] = 6     (Reload, um den STA sichtbar zu machen)
OUT          ; OUT ← AX
HLT