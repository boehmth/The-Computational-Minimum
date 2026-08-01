# ============================================================
#  Hilfsfunktionen fuer die Auswertung
# ============================================================


def evaluate(modell, merkmale, labels, name="Test"):
    """Wertet das Modell auf einem Datensatz aus und gibt eine
    detaillierte Ergebnistabelle in der Konsole aus."""
    korrekt = 0

    print(f"\nErgebnisse ({name}):")
    print("x1 | x2 | Ziel | Vorhersage | korrekt?")
    print("-------------------------------------")

    for (x1, x2), ziel in zip(merkmale, labels):
        vorhersage = modell.vorhersagen(x1, x2)
        if vorhersage == ziel:
            korrekt += 1

        print(f"{x1:2d} | {x2:2d} |  {ziel}   |     {vorhersage}      |  "
              f"{'ok' if vorhersage == ziel else 'X'}")

    genauigkeit = korrekt / len(labels)
    print(f"\n{name}-Genauigkeit: {genauigkeit * 100:.1f}%")