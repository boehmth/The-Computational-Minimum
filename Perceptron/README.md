# AI Milestone 1: The Perceptron

## 📖 Introduction
In 1958, psychologist **Frank Rosenblatt** introduced the *Perceptron* in his landmark paper *“The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain”* (Psychological Review, Vol. 65, No. 6, pp. 386–408). This work is widely regarded as the **first algorithmically described neural network**, bridging psychology, neuroscience, and computer science.

Rosenblatt, working at the **Cornell Aeronautical Laboratory** in Buffalo, New York, combined insights from psychology, neuroscience, and computing. His interdisciplinary background allowed him to conceptualize the perceptron not only as a mathematical model but also as a step toward understanding how the brain might process information.  

The perceptron demonstrated that machines could **learn to classify patterns** by adjusting weights based on errors, foreshadowing modern machine learning. Rosenblatt even built a hardware implementation, the *Mark I Perceptron*, which could recognize simple visual patterns. While limited to linearly separable problems (it could not solve tasks like XOR), its publication marked a **milestone in artificial intelligence research**, sparking decades of exploration into neural networks.

In this milestone we implement a simple **Perceptron** to learn the rule:

> **Is the first number smaller than the second?**

This is a linearly separable problem: the decision boundary is the line  

$x_1 = x_2$
  
in the two-dimensional input space. All points below this line (where $x_1 < x_2$) belong to class `1`, all points on or above the line belong to class `0`. We will see that this rather simplistic rule already allows for implementing powerful tasks, but it also shows the basic principles of modern machine learning, i.e.

- **learning from data rather than explicit rules**,  
- **adjusting parameters (weights and bias) based on errors**,  
- **iteratively improving performance over multiple training epochs**, and  
- **generalizing beyond the examples seen during training**.

Even though the perceptron is a very simple model, it already captures the essence of what makes machine learning powerful: the ability to discover structure in data through repeated exposure and incremental updates. In this milestone, we implement and explore this mechanism in its purest form, using a minimal dataset and a transparent learning rule to illustrate how a machine can learn a decision boundary from scratch.

---

## 🎯 Learning goals
- Understand how a perceptron separates two classes with a straight line.  
- Observe how weights and bias adapt during training.  
- Interpret the learned parameters: one weight becomes negative (for the first number), the other positive (for the second number).  
- Recognize the **limits of the perceptron**: it only works for linearly separable problems.  
- See how the **amount and diversity of training data** affect generalisation accuracy.  

## 📊 Conceptual diagram

This diagram shows the perceptron in its simplest form for this milestone: it takes **two inputs** (the two numbers to be compared), multiplies each by a **weight** (W1, W2), adds a **bias**, and then passes the result through a **step function** to produce a binary output (0 or 1).

```

   x1 (first number) ----->(W1)---\
                                   +--> [ SUMMATION + BIAS ] --> [ STEP FUNCTION ] --> OUTPUT (0/1)
   x2 (second number) ---->(W2)---/

```

In the general case, a perceptron can have any number of inputs $x_1, x_2, \dots, x_n$ with corresponding weights $w_1, w_2, \dots, w_n$. The structure of the computation remains the same — only the number of input lines and weights grows. For this milestone, we deliberately restrict ourselves to two inputs to keep the geometry and the learned decision boundary easy to visualise in a 2D plane.

## ⚙️ Mathematical formulation

The perceptron computes its output as:

$$
y = f\Big(\sum_{i=1}^{n} w_i \cdot x_i + b\Big)
$$

- $x_i$: inputs (features)  
- $w_i$: weights (importance of each input)  
- $b$: bias (shifts the decision boundary)  
- $f(\cdot)$: activation function (here: step function → outputs `1` if ≥ 0, else `0`)  

Update rule:

$$
w_i \leftarrow w_i + \eta \cdot (t - y) \cdot x_i
$$

$$
b \leftarrow b + \eta \cdot (t - y)
$$

## ▶️ How to run the program
The Python code for this milestone is located in: `milestones/src/perceptron.py`

### Steps
1. Open a terminal and navigate to the project root.  
2. Run the program with:

    ```bash
    python src/perceptron.py
    ```

Observe the output:

The program prints the trained weights and bias after learning.

You will see how the perceptron adjusts its weights to correctly separate these cases.

## 🧩 Example task: visualising the training data

To understand the task geometrically, it helps to look at the labels as a **matrix**.  
Each row corresponds to a fixed value of **x₁**, each column to a fixed value of **x₂**.  
The label is `1` if $x_1$ < $x_2$, and `0` otherwise.

Below is the label matrix for the range **3–9**:

```
      x2 →     3  4  5  6  7  8  9
x1 ↓
3           [ 0  1  1  1  1  1  1 ]
4           [ 0  0  1  1  1  1  1 ]
5           [ 0  0  0  1  1  1  1 ]
6           [ 0  0  0  0  1  1  1 ]
7           [ 0  0  0  0  0  1  1 ]
8           [ 0  0  0  0  0  0  1 ]
9           [ 0  0  0  0  0  0  0 ]
```


This matrix makes the structure of the task visible:

- All `1`s lie **above** the diagonal $x_1$ = $x_2$.  
- All `0`s lie **on or below** that diagonal.  
- The decision boundary is therefore a **straight line** through the matrix.  

This visualisation shows that the rule $x_1$ < $x_2$ is fundamentally a **geometric separation problem**, which is exactly what a perceptron is designed to learn.




## 📈 Example output (Learning rate = 0.01)

The following example uses the small training dataset (4–7). Because the perceptron only sees a limited range of input pairs during training, it does not fully generalise to the test range (10–12). This is intentional: the example illustrates how reduced training diversity leads to imperfect generalisation, even for a linearly separable problem.

```

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

```

## 📝 Exercises

### **1. Use the expanded linear dataset (all pairs from 3–9)**

Switch the dataset to the fully expanded version: ```python train_features, train_labels = get_large_dataset()```.This dataset contains all pairs ($x_1$, $x_2$) for numbers 3–9, giving the perceptron a broad and diverse set of examples for the linear rule $x_1$ < $x_2$.

**What to observe:**
- Fast and stable convergence
- Meaningful weights
- Strong generalisation to unseen values (e.g., 10–12)

**Learning goal:**
A perceptron performs well when the problem is linearly separable and the training data covers the relevant input space.

### **2. Use the circle dataset (contradictory / non‑linear example)**

Replace the dataset selection with: ```python train_features, train_labels = get_circle_dataset()```
This dataset labels points inside a circle as 1 and points outside as 0. No straight line can separate these two regions.

**What to observe:**
- The perceptron fails to converge
- Accuracy stagnates or fluctuates
- The learned weights do not form a meaningful decision boundary

Note: For the circle dataset, you do not need a separate test set. The perceptron already fails to learn the pattern on the training data itself,  
so evaluating on a test set would not provide additional insight. If you do use a test set, it must also consist of circle data.


**Learning goal:**
- This exercise demonstrates the fundamental limitation of the perceptron: it cannot learn non‑linear decision boundaries, regardless of training time.

## 🧪 Key observations

The following observations summarise what you should see when running the two exercises above:

- With the **expanded linear dataset (all pairs from 3–10)**, the perceptron converges quickly, learns stable weights, and generalises well to unseen values. This demonstrates that a linearly separable problem is solved reliably when the training data covers the relevant input space.

- With the **circle dataset**, the perceptron fails to converge because the pattern is not linearly separable. Accuracy fluctuates, the weights do not stabilise, and the learned decision boundary remains meaningless. In practice, the perceptron reaches an accuracy of about 50%. This happens because the true decision boundary is circular, while a perceptron can only learn a straight line. Any straight line cuts the circle into two regions of comparable size, so the model inevitably misclassifies roughly half of the points. In other words, the best possible linear separator performs no better than random guessing.

- Even for linear problems, **insufficient or poorly distributed training data** can reduce accuracy — as seen in the example output using the small dataset.

- In practical machine‑learning scenarios, models rarely achieve perfect accuracy; the perceptron is no exception, especially when data is limited or contradictory.


## 🧠 Closing remarks

The perceptron implemented in this milestone illustrates a fundamental geometric fact:  
a single-layer perceptron is always a **linear classifier**. It computes a weighted sum

$$
w_1 x_1 + w_2 x_2 + \dots + w_n x_n + b
$$

and applies a step function to decide between two classes. The equation

$$
w_1 x_1 + w_2 x_2 + \dots + w_n x_n + b = 0
$$

defines a **hyperplane** in an \(n\)-dimensional space — a line in 2D, a plane in 3D, and a linear separating surface in any number of dimensions.  
As a consequence, a perceptron can only learn **linearly separable** patterns.

This explains why the model succeeds on the rule *x₁ < x₂*: the decision boundary is a straight line.  
But it also explains why the perceptron fails on the circle dataset: no single line (or plane, or hyperplane) can separate the inside of a circle (or sphere) from the outside. This limitation is not an implementation detail but a fundamental representational constraint.

This insight was formalized by **Minsky & Papert (1969)** in their influential book *Perceptrons*, where they proved that single-layer perceptrons cannot represent non-linear functions such as parity, symmetry, or simple geometric shapes. Their analysis marked a turning point in the history of neural networks and motivated the development of **multi-layer architectures** capable of learning non-linear decision boundaries.

In the next milestone, we extend the perceptron into a **multi-layer perceptron (MLP)** and introduce the **backpropagation algorithm**, enabling the network to learn complex, non-linear patterns such as circles, letters, or arbitrary shapes.


## 📚 References

Hodgkin, A. L., & Huxley, A. F. (1952). *A quantitative description of membrane current and its application to conduction and excitation in nerve*. Journal of Physiology, 117(4), 500–544.

Minsky, M., & Papert, S. (1969). *Perceptrons: An Introduction to Computational Geometry*. MIT Press.

Rosenblatt, F. (1958). *The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain*. Psychological Review, 65(6), 386–408.

