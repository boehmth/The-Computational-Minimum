# Perceptron classification: "x1 < x2" with static train/test sets

LEARNING_RATE = 0.01
EPOCHS = 5

class Perceptron:
    """
    Einfaches Perzeptron zur Klassifikation von Zahlenpaaren (x1 < x2).
    """
    def __init__(self, learning_rate=LEARNING_RATE, epochs=EPOCHS):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights = [0.0, 0.0]
        self.bias = 0.0

    def step(self, x):
        """Aktivierungsfunktion: Step (Schwellwert)."""
        return 1 if x >= 0 else 0

    def forward(self, x1, x2):
        """Lineare Kombination der Eingaben mit Gewichten und Bias."""
        return (self.weights[0] * x1) + (self.weights[1] * x2) + self.bias

    def train(self, features, labels):
        """Trainiert das Perzeptron mit dem Perzeptron-Lernalgorithmus."""
        for epoch in range(self.epochs):
            errors_in_epoch = 0
            for (x1, x2), target in zip(features, labels):
                linear_output = self.forward(x1, x2)
                prediction = self.step(linear_output)
                error = target - prediction

                if error != 0:
                    errors_in_epoch += 1
                    # Update-Regel
                    self.weights[0] += self.learning_rate * error * x1
                    self.weights[1] += self.learning_rate * error * x2
                    self.bias += self.learning_rate * error

            accuracy = 1 - errors_in_epoch / len(features)
            w_str = [f"{w:.2f}" for w in self.weights]
            print(f"Epoch {epoch+1:2d}: errors={errors_in_epoch}, "
                  f"accuracy={accuracy:.2f}, weights={w_str}, bias={self.bias:.2f}")

    def predict(self, x1, x2):
        """Berechnet die Vorhersage für ein Zahlenpaar."""
        return self.step(self.forward(x1, x2))


def evaluate(model, features, labels, name="Test"):
    """Evaluierung des Modells auf einem Datensatz."""
    correct = 0
    print(f"\n{name} results:")
    print("x1 | x2 | target | pred | correct?")
    print("-----------------------------------")
    for (x1, x2), target in zip(features, labels):
        pred = model.predict(x1, x2)
        if pred == target:
            correct += 1
        print(f"{x1:2d} | {x2:2d} |   {target}    |   {pred}   | {'✓' if pred==target else '✗'}")
    accuracy = correct / len(labels)
    print(f"\n{name} accuracy: {accuracy*100:.1f}%")


def get_small_dataset():
    # Trainingsdaten: Zahlen 4–7
    train_features = [
        (4, 4), (4, 5), (4, 6), (4, 7),
        (5, 4), (5, 5), (5, 6), (5, 7),
        (6, 4), (6, 5), (6, 6), (6, 7),
        (7, 4), (7, 5), (7, 6), (7, 7)
    ]
    train_labels = [
        0,1,1,1,
        0,0,1,1,
        0,0,0,1,
        0,0,0,0
    ]
    return train_features, train_labels

def get_large_dataset():
    # Trainingsdaten: Zahlen 3–9
    train_features = [
        (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9),
        (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
        (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9),
        (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9),
        (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9),
        (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (8, 9),
        (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9)
    ]

    # Labels explizit ausgeschrieben: 1 wenn x1 < x2, sonst 0
    train_labels = [
        0,1,1,1,1,1,1,   # Zeile x1=3
        0,0,1,1,1,1,1,   # Zeile x1=4
        0,0,0,1,1,1,1,   # Zeile x1=5
        0,0,0,0,1,1,1,   # Zeile x1=6
        0,0,0,0,0,1,1,   # Zeile x1=7
        0,0,0,0,0,0,1,   # Zeile x1=8
        0,0,0,0,0,0,0    # Zeile x1=9
    ]
    return train_features, train_labels

def get_circle_dataset():
    # Trainingsdaten: Zahlen 3–9
    train_features = [
        (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9),
        (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
        (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9),
        (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9),
        (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9),
        (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (8, 9),
        (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9)
    ]

    circle_labels = [
        0,0,0,0,0,0,0,0,0,
        0,0,0,1,1,1,0,0,0,
        0,0,1,1,1,1,1,0,0,
        0,1,1,1,1,1,1,1,0,
        0,1,1,1,1,1,1,1,0,
        0,1,1,1,1,1,1,1,0,
        0,0,1,1,1,1,1,0,0,
        0,0,0,1,1,1,0,0,0,
        0,0,0,0,0,0,0,0,0
    ]
    return train_features, circle_labels

def main():
    # Trainingsdaten: Zahlen 3–9 als statisches Raster
    # Option wählen: klein oder groß
    use_large_dataset = True  # <--- hier umschalten

    if use_large_dataset:
        train_features, train_labels = get_large_dataset()
        print("Training mit großem Datensatz (3–9)")
    else:
        train_features, train_labels = get_small_dataset()
        print("Training mit kleinem Datensatz (4–7)")

    # Testdaten: Zahlen 10–12 als statisches Raster
    test_features = [
        (10, 10), (10, 11), (10, 12),
        (11, 10), (11, 11), (11, 12),
        (12, 10), (12, 11), (12, 12)
    ]

    test_labels = [
        0, 1, 1,   # Zeile x1=10
        0, 0, 1,   # Zeile x1=11
        0, 0, 0    # Zeile x1=12
    ]

    model = Perceptron()
    model.train(train_features, train_labels)

    print("\nFinal trained parameters:")
    print(f"Weights={[f'{w:.2f}' for w in model.weights]}, Bias={model.bias:.2f}")

    evaluate(model, test_features, test_labels, name="Test")

if __name__ == "__main__":
    main()

