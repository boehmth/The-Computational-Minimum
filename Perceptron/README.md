# Milestone 1: The Perceptron

## 📖 Introduction
In 1958, psychologist **Frank Rosenblatt** introduced the *Perceptron* in his landmark paper *“The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain”* (Psychological Review, Vol. 65, No. 6, pp. 386–408). This work is widely regarded as the **first algorithmically described neural network**, bridging psychology, neuroscience, and computer science.

Rosenblatt, working at the **Cornell Aeronautical Laboratory** in Buffalo, New York, combined insights from psychology, neuroscience, and computing. His interdisciplinary background allowed him to conceptualize the perceptron not only as a mathematical model but also as a step toward understanding how the brain might process information.  

The perceptron demonstrated that machines could **learn to classify patterns** by adjusting weights based on errors, foreshadowing modern machine learning. Rosenblatt even built a hardware implementation, the *Mark I Perceptron*, which could recognize simple visual patterns. While limited to linearly separable problems (it could not solve tasks like XOR), its publication marked a **milestone in artificial intelligence research**, sparking decades of exploration into neural networks.

In this milestone we implement a simple **Perceptron** to learn the rule:

> **Is the first number smaller than the second?**

This is a linearly separable problem: the decision boundary is the line  

\[
x_1 = x_2
\]
  
in the two-dimensional input space. All points below this line (where \(x_1 < x_2\)) belong to class `1`, all points on or above the line belong to class `0`.

---

## 🎯 Learning goals
- Understand how a perceptron separates two classes with a straight line.  
- Observe how weights and bias adapt during training.  
- Interpret the learned parameters: one weight becomes negative (for the first number), the other positive (for the second number).  
- Recognize the **limits of the perceptron**: it only works for linearly separable problems.  
- See how the **amount and diversity of training data** affect generalisation accuracy.  

---

## ▶️ How to run the program
The Python code for this milestone is located in:

milestones/src/perceptron.py

### Steps
1. Open a terminal and navigate to the project root.  
2. Run the program with:  
   ```bash
   python milestones/src/perceptron.py

Observe the output:

The program prints the trained weights and bias after learning.

You will see how the perceptron adjusts its weights to correctly separate these cases.

## 📊 Conceptual diagram

   x1 (first number) ----->(W1)---\
                                   +--> [ SUMMATION + BIAS ] --> [ STEP FUNCTION ] --> OUTPUT (0/1)
   x2 (second number) ---->(W2)---/
     

## ⚙️ Mathematical formulation

The perceptron computes its output as:

$$
y = f\Big(\sum_{i=1}^{n} w_i \cdot x_i + b\Big)
$$

- \(x_i\): inputs (features)  
- \(w_i\): weights (importance of each input)  
- \(b\): bias (shifts the decision boundary)  
- \(f(\cdot)\): activation function (here: step function → outputs `1` if ≥ 0, else `0`)  

Update rule:

$$
w_i \leftarrow w_i + \eta \cdot (t - y) \cdot x_i
$$

$$
b \leftarrow b + \eta \cdot (t - y)
$$

## 📈 Example output (Learning rate = 0.01)

Epoch  1: errors=7, accuracy=0.56, weights=['-0.07', '0.02'], bias=-0.01
Epoch  2: errors=6, accuracy=0.62, weights=['-0.10', '0.08'], bias=-0.01
Epoch  3: errors=4, accuracy=0.75, weights=['-0.12', '0.11'], bias=-0.01
Epoch  4: errors=0, accuracy=1.00, weights=['-0.12', '0.11'], bias=-0.01
Epoch  5: errors=0, accuracy=1.00, weights=['-0.12', '0.11'], bias=-0.01

Weights=[-0.12, 0.11], Bias=-0.01

x1 | x2 | target | pred | correct?
-----------------------------------
10 | 10 |   0    |   0   | ✓
10 | 11 |   1    |   0   | ✗
10 | 12 |   1    |   1   | ✓
11 | 10 |   0    |   0   | ✓
11 | 11 |   0    |   0   | ✓
11 | 12 |   1    |   0   | ✗
12 | 10 |   0    |   0   | ✓
12 | 11 |   0    |   0   | ✓
12 | 12 |   0    |   0   | ✓

Test accuracy: 77.8%

## 🧪 Key observations
With full training coverage (e.g. numbers 1–7), the perceptron learns the rule almost perfectly and generalises well.

With reduced training coverage (e.g. only 4–7), the model achieves ~88.9% accuracy on test data (10–12).

This illustrates:

Dependence on training data: fewer examples → less stable weights → imperfect generalisation.

Limits of the perceptron: even for linearly separable problems, insufficient data can lead to errors.

Realism: in practice, models rarely achieve 100% accuracy.

## 📝 Exercises

Expand the dataset: Generate all pairs (x1, x2) for numbers 1–10.

Visualize: Plot the points in a 2D plane and draw the learned decision boundary.

Interpret weights: Check that the weight for x1 is negative and for x2 positive.

Change the rule: Modify the target to x1 > x2 and retrain. Observe how the weights flip.

Noise: Add contradictory examples (e.g. [2, 6] labeled as 0) and see how the perceptron struggles.

## 🧠 Closing remarks
The perceptron is more than just a mathematical curiosity. It represents a reductionist model of a biological neuron: inputs are weighted, summed, and passed through a threshold to produce an output. This abstraction mirrors the scientific understanding of the time, when neurophysiologists such as Alan Hodgkin and Andrew Huxley had already described how nerve cells integrate signals and fire an action potential once a critical threshold is reached.

By deliberately simplifying the biochemical and temporal complexity of real neurons, Rosenblatt created a model that was both tractable for computation and faithful to the essential principle of neuronal firing. This reductionism was not a weakness but a strength: it allowed the perceptron to become the first formal framework for machine learning, inspiring generations of researchers to build more sophisticated architectures.

## 📚 References
Rosenblatt, F. (1958). The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain. Psychological Review, 65(6), 386–408.

Hodgkin, A. L., & Huxley, A. F. (1952). A quantitative description of membrane current and its application to conduction and excitation in nerve. Journal of Physiology, 117(4), 500–544.