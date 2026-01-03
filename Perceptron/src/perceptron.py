# ============================================================
#  AI Milestone 1 — The Perceptron
#  Classification task: "x1 < x2"
#  Demonstrates linear separability and model limitations
# ============================================================

from datasets import DatasetFactory
from utils import evaluate

DATASET_MODE = "circle"  # Options: "small", "large", "circle"
LEARNING_RATE = 0.01
EPOCHS = 5

# ============================================================
#  Perceptron Model
# ============================================================

class Perceptron:
    """
    A simple perceptron for classifying number pairs (x1 < x2).
    """

    def __init__(self, learning_rate=LEARNING_RATE, epochs=EPOCHS):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights = [0.0, 0.0]
        self.bias = 0.0

    def step(self, x):
        """Step activation function."""
        return 1 if x >= 0 else 0

    def forward(self, x1, x2):
        """Linear combination of inputs and bias."""
        return (self.weights[0] * x1) + (self.weights[1] * x2) + self.bias

    def train(self, features, labels):
        """Train the perceptron using the perceptron learning rule."""
        for epoch in range(self.epochs):
            errors_in_epoch = 0

            for (x1, x2), target in zip(features, labels):
                linear_output = self.forward(x1, x2)
                prediction = self.step(linear_output)
                error = target - prediction

                if error != 0:
                    errors_in_epoch += 1
                    self.weights[0] += self.learning_rate * error * x1
                    self.weights[1] += self.learning_rate * error * x2
                    self.bias += self.learning_rate * error

            accuracy = 1 - errors_in_epoch / len(features)
            w_str = [f"{w:.2f}" for w in self.weights]

            print(
                f"Epoch {epoch+1:2d}: errors={errors_in_epoch}, "
                f"accuracy={accuracy:.2f}, weights={w_str}, bias={self.bias:.2f}"
            )

    def predict(self, x1, x2):
        """Predict the class for a pair (x1, x2)."""
        return self.step(self.forward(x1, x2))


# ============================================================
#  Main Experiment Runner
# ============================================================

def main():
    # --------------------------------------------------------
    # 1. Select dataset mode
    #    Options:
    #       "small"  – linear dataset (4–7)
    #       "large"  – linear dataset (3–9)
    #       "circle" – non-linear dataset (perceptron fails)
    # --------------------------------------------------------
    dataset_mode = DATASET_MODE   # <--- switch here

    # --------------------------------------------------------
    # 2. Load training and test data via DatasetFactory
    # --------------------------------------------------------
    (train_features, train_labels), (test_features, test_labels) = DatasetFactory.get(dataset_mode)

    print(f"Training with dataset mode: {dataset_mode}")

    # --------------------------------------------------------
    # 3. Train the perceptron model
    # --------------------------------------------------------
    model = Perceptron()
    model.train(train_features, train_labels)

    # --------------------------------------------------------
    # 4. Print final learned parameters
    # --------------------------------------------------------
    print("\nFinal trained parameters:")
    print(f"Weights={[f'{w:.2f}' for w in model.weights]}, Bias={model.bias:.2f}")

    # --------------------------------------------------------
    # 5. Evaluate the model
    # --------------------------------------------------------
    evaluate(model, test_features, test_labels, name="Test")


# ============================================================
#  Entry Point
# ============================================================

if __name__ == "__main__":
    main()
