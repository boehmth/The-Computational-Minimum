# ============================================================
#  Buchstaben-Datensatz-Fabrik (9x9-Bitmaps)
# ============================================================


class LetterDatasetFactory:
    """
    Liefert 9x9-Bitmaps fuer die Buchstaben A, L, R.

    Rueckgabe:
        data:            Liste von flachen 81-elementigen Pixelvektoren
        labels:          Liste von One-Hot-Zielvektoren
        index_to_letter: Zuordnung Ausgabe-Index -> Buchstabe
    """

    @staticmethod
    def get_letters():
        bitmaps = {
            "A": [
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 1, 1, 1, 0, 0, 0,
                0, 0, 1, 1, 1, 1, 1, 0, 0,
                0, 1, 1, 0, 0, 0, 1, 1, 0,
                0, 1, 1, 0, 0, 0, 1, 1, 0,
                0, 1, 1, 1, 1, 1, 1, 1, 0,
                0, 1, 1, 1, 1, 1, 1, 1, 0,
                0, 1, 1, 0, 0, 0, 1, 1, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0,
            ],
            "L": [
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 1, 1, 0, 0, 0, 0, 0, 0,
                0, 1, 1, 0, 0, 0, 0, 0, 0,
                0, 1, 1, 0, 0, 0, 0, 0, 0,
                0, 1, 1, 0, 0, 0, 0, 0, 0,
                0, 1, 1, 0, 0, 0, 1, 1, 0,
                0, 1, 1, 1, 1, 1, 1, 1, 0,
                0, 1, 1, 1, 1, 1, 1, 1, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0,
            ],
            "R": [
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 1, 1, 1, 1, 1, 0, 0, 0,
                0, 1, 1, 0, 0, 1, 1, 0, 0,
                0, 1, 1, 0, 0, 1, 1, 0, 0,
                0, 1, 1, 1, 1, 1, 0, 0, 0,
                0, 1, 1, 0, 1, 1, 0, 0, 0,
                0, 1, 1, 0, 0, 1, 1, 0, 0,
                0, 1, 1, 0, 0, 0, 1, 1, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0,
            ],
        }

        buchstaben = ["A", "L", "R"]
        daten = [bitmaps[ch] for ch in buchstaben]

        # One-Hot-Kodierung: A = 0, L = 1, R = 2
        labels = []
        for i in range(len(buchstaben)):
            vec = [0] * len(buchstaben)
            vec[i] = 1
            labels.append(vec)

        return daten, labels, buchstaben