; Kanonische Aufgabe: (3+4)-1 in LISP-Manier.
; Zeigt die "es-ist-alles-eine-Liste"-Notation von McCarthy (1958).

(defun main ()
  (let ((x 3) (y 4))
    (let ((z (- (+ x y) 1)))
      (print z))))

(main)