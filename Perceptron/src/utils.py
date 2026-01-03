
# ============================================================
#  Evaluation Utility
# ============================================================

def evaluate(model, features, labels, name="Test"):
    """Evaluate the model on a dataset and print detailed results."""
    correct = 0

    print(f"\n{name} results:")
    print("x1 | x2 | target | pred | correct?")
    print("-----------------------------------")

    for (x1, x2), target in zip(features, labels):
        pred = model.predict(x1, x2)
        if pred == target:
            correct += 1

        print(f"{x1:2d} | {x2:2d} |   {target}    |   {pred}   | "
              f"{'✓' if pred == target else '✗'}")

    accuracy = correct / len(labels)
    print(f"\n{name} accuracy: {accuracy * 100:.1f}%")
