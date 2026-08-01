# ============================================================
#  Datensatz-Fabrik (DatasetFactory)
#
#  Liefert Trainings- und Testdaten fuer den Perceptron-
#  Meilenstein - je nach Modus:
#     "small"  - linear, kleiner Bereich (4-7)
#     "large"  - linear, groesserer Bereich (3-9)
#     "circle" - nicht-linear (Kreis), zeigt Perceptron-Grenze
# ============================================================


class DatasetFactory:
    """
    Fabrik zur Erzeugung verschiedener Trainings- und Testdatensaetze.

    Modi:
        - "small"   : linear, eingeschraenkter Bereich (4-7)
        - "large"   : linear, vollstaendiger Bereich (3-9)
        - "circle"  : nicht-linear, das Perceptron scheitert daran
    """

    @staticmethod
    def get(modus):
        if modus == "small":
            return DatasetFactory._kleiner_datensatz(), DatasetFactory._linearer_testsatz()
        elif modus == "large":
            return DatasetFactory._grosser_datensatz(), DatasetFactory._linearer_testsatz()
        elif modus == "circle":
            # Beim Kreis-Datensatz sind Trainings- und Testdaten identisch,
            # da das Perceptron schon auf den Trainingsdaten scheitert.
            training = DatasetFactory._kreis_datensatz()
            return training, training
        else:
            raise ValueError(f"Unbekannter Datensatzmodus: {modus}")

    # --------------------------------------------------------
    # Interne Erzeugungsfunktionen
    # --------------------------------------------------------

    @staticmethod
    def _kleiner_datensatz():
        merkmale = [
            (4, 4), (4, 5), (4, 6), (4, 7),
            (5, 4), (5, 5), (5, 6), (5, 7),
            (6, 4), (6, 5), (6, 6), (6, 7),
            (7, 4), (7, 5), (7, 6), (7, 7),
        ]
        labels = [
            0, 1, 1, 1,
            0, 0, 1, 1,
            0, 0, 0, 1,
            0, 0, 0, 0,
        ]
        return merkmale, labels

    @staticmethod
    def _grosser_datensatz():
        merkmale = [(x1, x2) for x1 in range(3, 10) for x2 in range(3, 10)]
        labels = [
            0, 1, 1, 1, 1, 1, 1,   # Zeile x1 = 3
            0, 0, 1, 1, 1, 1, 1,   # Zeile x1 = 4
            0, 0, 0, 1, 1, 1, 1,   # Zeile x1 = 5
            0, 0, 0, 0, 1, 1, 1,   # Zeile x1 = 6
            0, 0, 0, 0, 0, 1, 1,   # Zeile x1 = 7
            0, 0, 0, 0, 0, 0, 1,   # Zeile x1 = 8
            0, 0, 0, 0, 0, 0, 0,   # Zeile x1 = 9
        ]
        return merkmale, labels

    @staticmethod
    def _linearer_testsatz():
        merkmale = [
            (10, 10), (10, 11), (10, 12),
            (11, 10), (11, 11), (11, 12),
            (12, 10), (12, 11), (12, 12),
        ]
        labels = [
            0, 1, 1,
            0, 0, 1,
            0, 0, 0,
        ]
        return merkmale, labels

    @staticmethod
    def _kreis_datensatz():
        merkmale = [(x1, x2) for x1 in range(1, 10) for x2 in range(1, 10)]

        # 9x9-Kreismaske (zentriert)
        kreis_labels = [
            0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 1, 1, 1, 0, 0, 0,
            0, 0, 1, 1, 1, 1, 1, 0, 0,
            0, 1, 1, 1, 1, 1, 1, 1, 0,
            0, 1, 1, 1, 1, 1, 1, 1, 0,
            0, 1, 1, 1, 1, 1, 1, 1, 0,
            0, 0, 1, 1, 1, 1, 1, 0, 0,
            0, 0, 0, 1, 1, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0,
        ]
        return merkmale, kreis_labels