# ============================================================
#  KI-Meilenstein 1 - Das Perceptron
#  Klassifikationsaufgabe: "x1 < x2"
#  Zeigt lineare Trennbarkeit und die Grenzen des Modells.
# ============================================================

from datasets import DatasetFactory
from utils import evaluate

DATASET_MODE = "large"   # Optionen: "small", "large", "circle"
LERNRATE = 0.01
EPOCHEN = 5


# ============================================================
#  Das Perceptron-Modell
# ============================================================

class Perceptron:
    """
    Ein einfaches Perceptron zur Klassifikation von Zahlenpaaren (x1 < x2).
    """

    def __init__(self, lernrate=LERNRATE, epochen=EPOCHEN):
        self.lernrate = lernrate
        self.epochen = epochen
        self.gewichte = [0.0, 0.0]
        self.bias = 0.0

    def sprungfunktion(self, x):
        """Sprungfunktion als Aktivierung."""
        return 1 if x >= 0 else 0

    def vorwaerts(self, x1, x2):
        """Gewichtete Summe der Eingaben plus Bias."""
        return (self.gewichte[0] * x1) + (self.gewichte[1] * x2) + self.bias

    def trainieren(self, merkmale, labels):
        """Trainiert das Perceptron mit der klassischen Perceptron-Lernregel."""
        for epoche in range(self.epochen):
            fehler_in_epoche = 0

            for (x1, x2), ziel in zip(merkmale, labels):
                lineare_ausgabe = self.vorwaerts(x1, x2)
                vorhersage = self.sprungfunktion(lineare_ausgabe)
                fehler = ziel - vorhersage

                if fehler != 0:
                    fehler_in_epoche += 1
                    self.gewichte[0] += self.lernrate * fehler * x1
                    self.gewichte[1] += self.lernrate * fehler * x2
                    self.bias += self.lernrate * fehler

            genauigkeit = 1 - fehler_in_epoche / len(merkmale)
            g_str = [f"{g:.2f}" for g in self.gewichte]

            print(
                f"Epoche {epoche + 1:2d}: Fehler={fehler_in_epoche}, "
                f"Genauigkeit={genauigkeit:.2f}, Gewichte={g_str}, Bias={self.bias:.2f}"
            )

    def vorhersagen(self, x1, x2):
        """Sagt die Klasse fuer ein Paar (x1, x2) voraus."""
        return self.sprungfunktion(self.vorwaerts(x1, x2))


# ============================================================
#  Hauptprogramm
# ============================================================

def main():
    # --------------------------------------------------------
    # 1. Datensatzmodus waehlen
    #    Optionen:
    #       "small"  - kleiner linearer Datensatz (4-7)
    #       "large"  - grosser linearer Datensatz (3-9)
    #       "circle" - nicht-linearer Datensatz (Perceptron scheitert)
    # --------------------------------------------------------
    datensatz_modus = DATASET_MODE

    # --------------------------------------------------------
    # 2. Trainings- und Testdaten ueber DatasetFactory laden
    # --------------------------------------------------------
    (train_merkmale, train_labels), (test_merkmale, test_labels) = \
        DatasetFactory.get(datensatz_modus)

    print(f"Training mit Datensatzmodus: {datensatz_modus}")

    # --------------------------------------------------------
    # 3. Das Perceptron trainieren
    # --------------------------------------------------------
    modell = Perceptron()
    modell.trainieren(train_merkmale, train_labels)

    # --------------------------------------------------------
    # 4. Gelernte Parameter ausgeben
    # --------------------------------------------------------
    print("\nGelernte Parameter:")
    print(f"Gewichte={[f'{g:.2f}' for g in modell.gewichte]}, Bias={modell.bias:.2f}")

    # --------------------------------------------------------
    # 5. Modell auf den Testdaten evaluieren
    # --------------------------------------------------------
    evaluate(modell, test_merkmale, test_labels, name="Test")


# ============================================================
#  Einstiegspunkt
# ============================================================

if __name__ == "__main__":
    main()