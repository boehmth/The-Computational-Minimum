# AI Milestone 2: The Multi‑Layer Perceptron (MLP)

## 📖 Introduction

The Perceptron introduced the idea of **learning from data**, but it was limited to **linear** decision boundaries.  
To recognize more complex patterns, we need a model capable of learning **non‑linear relationships**.

This brings us to the **Multi‑Layer Perceptron (MLP)** — the first true step toward modern Deep Learning.

In this chapter, we will:

- build an **MLP from scratch**  
- implement **forward pass**, **backpropagation**, and **gradient descent**  
- train it on simple **9×9 bitmap characters** (A, L, R)  
- test robustness using **noise** and **shifts**  
- understand **why MLPs work — and where they fail**

## 🕰️ Historical Context: The Backpropagation Breakthrough (1986)

While the idea of multi‑layer neural networks existed since the 1960s, they were practically unusable for decades.  
The reason was simple:

> Nobody knew how to train the hidden layers.

This changed in 1986, when **David E. Rumelhart**, **Geoffrey E. Hinton**, and **Ronald J. Williams** published the landmark paper:

**“Learning representations by back‑propagating errors” (Nature, 1986)**

This paper introduced **Backpropagation**, the algorithm that made deep learning possible.

Backpropagation enabled:

- training networks with multiple layers  
- learning internal representations  
- solving non‑linear classification problems  
- the birth of modern neural networks  

It is no exaggeration to say:

> Backpropagation is the foundation of all modern AI —  
> CNNs, RNNs, Transformers, and LLMs all depend on it.

---


## 🧠 What the MLP Adds Beyond the Perceptron

The MLP introduces **hidden layers** and **non‑linear activation functions**.  
This allows the network to learn:

- curved decision boundaries  
- hierarchical features  
- distributed representations  
- complex patterns in data  

In our case:  
It allows the model to recognize **A, L, R** from 9×9 pixel grids.

---

## 🖼️ Dataset: 9×9 Bitmap Characters

We represent each character as a 9×9 grid of 0/1 values:

- 81 input features  
- simple enough to visualize  
- complex enough to require non‑linear learning  

Example (A):


---

## 🧩 Model Architecture

Our MLP consists of:

- **Input layer:** 81 neurons (one per pixel)  
- **Hidden layer:** e.g., 18 neurons  
- **Output layer:** 3 neurons (A, L, R)  

Activation functions:

- **Hidden layer:** Sigmoid  
- **Output layer:** Sigmoid (for confidence scores)

---

## 🔧 Training: Backpropagation + Gradient Descent

We train the network using:

- **Mean Squared Error (MSE)**  
- **Gradient Descent**  
- **Backpropagation** to compute gradients  

This is implemented manually — no frameworks.

---

## 🧪 Robustness Tests: Noise

We flip random pixels in the input bitmap:

- small noise → model stays correct  
- medium noise → confidence drops  
- large noise → model may misclassify  

Example:


This reveals:

- some pixels are important (high weights)  
- others are irrelevant (near‑zero weights)  
- noise pushes the input across the decision boundary  

---

## 🧪 Robustness Tests: Shifts

If we shift the bitmap by 1 pixel:

- the MLP fails completely  
- all characters collapse to the same prediction  
- confidence becomes low and unstable  

This demonstrates a key limitation:

> MLPs do not understand spatial structure.  
> They treat the image as a flat vector.

This motivates the next chapter: **Convolutional Neural Networks (CNNs)**.

---

## 🧠 Key Takeaways (Merksatz)

---

### **1. Non‑linearity**  
Hidden layers allow the MLP to learn curved, complex decision boundaries.

### **2. Distributed representations**  
Knowledge is stored across many weights — not in single neurons.

### **3. Feature importance**  
Some inputs matter far more than others; noise reveals this.

### **4. Robustness (limited)**  
MLPs tolerate small noise but fail under structural changes.

### **5. Global processing**  
The MLP sees the entire image at once — it has no concept of locality.

### **6. No translation invariance**  
A one‑pixel shift destroys the pattern — a major weakness.

---

## 📦 Files in This Chapter

- `mlp.py` — MLP implementation  
- `datasets.py` — 9×9 character bitmaps  
- `utils.py` — noise, shifting, helper functions  
- `main.py` — training and evaluation  

---

## 🚀 Next Chapter: Convolutional Neural Networks (CNNs)

CNNs solve the MLP’s biggest weaknesses:

- they learn **local features**  
- they share weights across the image  
- they are **translation invariant**  

This makes them the gold standard for image recognition — and the natural next step in our journey.


## 📚 Key References

**Primary historical source**  
- Rumelhart, Hinton & Williams (1986): *Learning representations by back‑propagating errors.*

**Additional foundational literature**  
- Werbos (1974): Early formulation of backpropagation  
- McClelland & Rumelhart (1986): *Parallel Distributed Processing*  
- Bishop (1995): *Neural Networks for Pattern Recognition*  
- Goodfellow, Bengio, Courville (2016): *Deep Learning* (Chapter 6)

