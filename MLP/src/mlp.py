# ============================================================
#  Multi-Layer Perceptron for 9x9 bitmap letters
# ============================================================

import random
from xml.parsers.expat import model
from utils import sigmoid, sigmoid_derivative, argmax_index, add_noise
from datasets import LetterDatasetFactory

LEARNING_RATE = 0.01
EPOCHS = 5000

class MLP_9x9:
    """
    Simple MLP with:
        - 81 input neurons (9x9 bitmap)
        - hidden_size hidden neurons
        - output_size output neurons (letters)
    """

    def __init__(self, hidden_size=20, output_size=3):
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Input -> Hidden
        self.w_input_hidden = [
            [random.uniform(-0.5, 0.5) for _ in range(81)]
            for _ in range(hidden_size)
        ]
        self.b_hidden = [0.0 for _ in range(hidden_size)]

        # Hidden -> Output
        self.w_hidden_output = [
            [random.uniform(-0.5, 0.5) for _ in range(hidden_size)]
            for _ in range(output_size)
        ]
        self.b_output = [0.0 for _ in range(output_size)]

    # --------------------------------------------------------
    # Forward pass
    # --------------------------------------------------------
    def forward(self, inputs):
        hidden_inputs = [
            sum(self.w_input_hidden[i][j] * inputs[j] for j in range(81)) + self.b_hidden[i]
            for i in range(self.hidden_size)
        ]
        hidden_outputs = [sigmoid(h) for h in hidden_inputs]

        output_inputs = [
            sum(self.w_hidden_output[k][i] * hidden_outputs[i] for i in range(self.hidden_size)) + self.b_output[k]
            for k in range(self.output_size)
        ]
        outputs = [sigmoid(o) for o in output_inputs]

        return hidden_outputs, outputs

    # --------------------------------------------------------
    # Training (Backpropagation)
    # --------------------------------------------------------
    def train(self, data, labels):
        for epoch in range(EPOCHS):
            total_error = 0

            for inputs, target_vec in zip(data, labels):
                hidden_outputs, outputs = self.forward(inputs)

                # Output errors
                errors = [t - o for t, o in zip(target_vec, outputs)]
                total_error += sum(e*e for e in errors)

                # Output deltas
                delta_output = [
                    e * sigmoid_derivative(o)
                    for e, o in zip(errors, outputs)
                ]

                # Hidden deltas
                delta_hidden = []
                for i in range(self.hidden_size):
                    back = sum(self.w_hidden_output[k][i] * delta_output[k]
                               for k in range(self.output_size))
                    delta_hidden.append(sigmoid_derivative(hidden_outputs[i]) * back)

                # Update Hidden -> Output
                for k in range(self.output_size):
                    for i in range(self.hidden_size):
                        self.w_hidden_output[k][i] += LEARNING_RATE * delta_output[k] * hidden_outputs[i]
                    self.b_output[k] += LEARNING_RATE * delta_output[k]

                # Update Input -> Hidden
                for i in range(self.hidden_size):
                    for j in range(81):
                        self.w_input_hidden[i][j] += LEARNING_RATE * delta_hidden[i] * inputs[j]
                    self.b_hidden[i] += LEARNING_RATE * delta_hidden[i]

            if epoch % 500 == 0:
                print(f"Epoch {epoch}: total_error={total_error:.4f}")

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------
    def predict(self, inputs):
        _, outputs = self.forward(inputs)
        idx = argmax_index(outputs)
        confidence = outputs[idx]
        return idx, confidence

# ============================================================
#  Main experiment
# ============================================================

def main():
    data, labels, index_to_letter = LetterDatasetFactory.get_letters()

    model = MLP_9x9(hidden_size=20, output_size=len(index_to_letter))
    model.train(data, labels)

    print("\n--- Predictions ---")
    for vec, letter in zip(data, index_to_letter):
        noisy = add_noise(vec, flips=30)
        pred_idx, conf = model.predict(noisy)
        print(f"{letter} → predicted {index_to_letter[pred_idx]} (confidence={conf:.2f})")

if __name__ == "__main__":
    main()
