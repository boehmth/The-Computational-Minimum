# ============================================================
#  Multi-Layer-Perzeptron (MLP) fuer 9x9-Bitmap-Buchstaben
#
#  Wir bauen alles selbst - Vorwaertsberechnung, Rueckwaerts-
#  propagation (Backprop) und Gradientenabstieg. Keine
#  Bibliothek uebernimmt die Rechnung. So bleibt jeder
#  einzelne Rechenschritt sichtbar.
# ============================================================

import random

from utils import sigmoid, sigmoid_derivative, argmax_index, add_noise
from datasets import LetterDatasetFactory


LERNRATE = 0.01
EPOCHEN = 5000


class MLP_9x9:
    """
    Ein einfaches MLP mit:
        - 81 Eingabe-Neuronen (9x9 Bitmap)
        - `hidden_size` verborgenen Neuronen (Sigmoid)
        - `output_size` Ausgabe-Neuronen (Sigmoid; einer pro Klasse)
    """

    def __init__(self, hidden_size=20, output_size=3):
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Gewichte: Eingabe -> verborgene Schicht
        self.w_eingabe_verborgen = [
            [random.uniform(-0.5, 0.5) for _ in range(81)]
            for _ in range(hidden_size)
        ]
        self.b_verborgen = [0.0 for _ in range(hidden_size)]

        # Gewichte: verborgene Schicht -> Ausgabe
        self.w_verborgen_ausgabe = [
            [random.uniform(-0.5, 0.5) for _ in range(hidden_size)]
            for _ in range(output_size)
        ]
        self.b_ausgabe = [0.0 for _ in range(output_size)]

    # --------------------------------------------------------
    # Vorwaertsberechnung
    # --------------------------------------------------------
    def forward(self, eingaben):
        """Berechnet einen kompletten Vorwaertsdurchlauf und
        gibt (Aktivierungen der verborgenen Schicht, Ausgaben) zurueck."""
        verborgen_eingang = [
            sum(self.w_eingabe_verborgen[i][j] * eingaben[j] for j in range(81))
            + self.b_verborgen[i]
            for i in range(self.hidden_size)
        ]
        verborgen_ausgang = [sigmoid(h) for h in verborgen_eingang]

        ausgabe_eingang = [
            sum(self.w_verborgen_ausgabe[k][i] * verborgen_ausgang[i]
                for i in range(self.hidden_size))
            + self.b_ausgabe[k]
            for k in range(self.output_size)
        ]
        ausgaben = [sigmoid(o) for o in ausgabe_eingang]

        return verborgen_ausgang, ausgaben

    # --------------------------------------------------------
    # Training via Backpropagation
    # --------------------------------------------------------
    def train(self, daten, labels):
        """Trainiert das Netz mit Gradientenabstieg + Backpropagation."""
        for epoche in range(EPOCHEN):
            gesamtfehler = 0.0

            for eingaben, zielvektor in zip(daten, labels):
                verborgen_ausgang, ausgaben = self.forward(eingaben)

                # Fehler an der Ausgangsschicht
                fehler = [t - o for t, o in zip(zielvektor, ausgaben)]
                gesamtfehler += sum(f * f for f in fehler)

                # Deltas der Ausgangsschicht
                delta_ausgabe = [
                    f * sigmoid_derivative(o)
                    for f, o in zip(fehler, ausgaben)
                ]

                # Deltas der verborgenen Schicht (Rueckweg)
                delta_verborgen = []
                for i in range(self.hidden_size):
                    zurueck = sum(
                        self.w_verborgen_ausgabe[k][i] * delta_ausgabe[k]
                        for k in range(self.output_size)
                    )
                    delta_verborgen.append(sigmoid_derivative(verborgen_ausgang[i]) * zurueck)

                # Gewichte verborgene Schicht -> Ausgabe aktualisieren
                for k in range(self.output_size):
                    for i in range(self.hidden_size):
                        self.w_verborgen_ausgabe[k][i] += (
                            LERNRATE * delta_ausgabe[k] * verborgen_ausgang[i]
                        )
                    self.b_ausgabe[k] += LERNRATE * delta_ausgabe[k]

                # Gewichte Eingabe -> verborgene Schicht aktualisieren
                for i in range(self.hidden_size):
                    for j in range(81):
                        self.w_eingabe_verborgen[i][j] += (
                            LERNRATE * delta_verborgen[i] * eingaben[j]
                        )
                    self.b_verborgen[i] += LERNRATE * delta_verborgen[i]

            if epoche % 500 == 0:
                print(f"Epoche {epoche}: Gesamtfehler={gesamtfehler:.4f}")

    # --------------------------------------------------------
    # Vorhersage
    # --------------------------------------------------------
    def predict(self, eingaben):
        """Gibt (Klassenindex, Vertrauen) fuer die Eingabe zurueck."""
        _, ausgaben = self.forward(eingaben)
        idx = argmax_index(ausgaben)
        vertrauen = ausgaben[idx]
        return idx, vertrauen


# ============================================================
#  Hauptprogramm
# ============================================================

def main():
    daten, labels, index_zu_buchstabe = LetterDatasetFactory.get_letters()

    modell = MLP_9x9(hidden_size=20, output_size=len(index_zu_buchstabe))
    modell.train(daten, labels)

    print("\n--- Vorhersagen bei leichtem Rauschen ---")
    for vektor, buchstabe in zip(daten, index_zu_buchstabe):
        verrauscht = add_noise(vektor, flips=30)
        vorhersage_idx, vertrauen = modell.predict(verrauscht)
        print(
            f"{buchstabe} -> vorhergesagt: {index_zu_buchstabe[vorhersage_idx]} "
            f"(Vertrauen={vertrauen:.2f})"
        )


if __name__ == "__main__":
    main()