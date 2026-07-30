"""
moe_layer.py - Sparsely-Gated Mixture of Experts als Drop-in-Ersatz fuer den FFN-Block

DIDAKTISCHE POINTE DIESES KAPITELS
==================================

In TinyGPT/TinyInstruct/TinyChat besteht ein Transformer-Block aus zwei
Teilen:
    x -> Attention -> LayerNorm -> FFN -> LayerNorm

Der FFN ist eine gewoehnliche Feed-Forward-Schicht: ALLE Parameter werden
fuer JEDES Token benutzt. Das ist der Kostentreiber.

MoE ersetzt diesen FFN durch:
    * N kleine FFN-Experten
    * ein Gating-Netzwerk, das pro Token die Top-k Experten auswaehlt
      (z.B. k=2 aus N=8)

Ergebnis: das Modell hat viele Gesamt-Parameter, aber pro Token nur
ungefaehr (k/N) davon aktiv. Kapazitaet waechst, Rechenkosten pro Token
bleiben.

Kern-Gefahr: Gating kollabiert. Ohne Gegenmassnahme lernt das Netz gerne,
IMMER dieselben ein oder zwei Experten zu waehlen, weil die anfangs
zufaellig etwas besseres tun. Die restlichen Experten bekommen dann nie
ein Gradient-Signal und lernen nichts. Loesung: ein zusaetzlicher
**Load-Balancing-Loss** (Shazeer et al. 2017), der bestraft, wenn ein
Experte zu haeufig gewaehlt wird.

WAS "DIE EINE ZEILE" DIESES KAPITELS IST
========================================

Es sind eigentlich ZWEI Zeilen, weil MoE aus zwei Ideen besteht:

1. Routing:
       gate_scores = gate_linear(x)
       top_vals, top_idx = topk(gate_scores, k)

2. Load-Balancing (die Zeile, die den Kollaps verhindert):
       aux_loss = num_experts * sum(fraction_i * routing_prob_i)

Alles andere ist Buchhaltung (Sparse-Matmul emulieren, Rueck-Aggregation,
Residual-Verbindungen).
"""

from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class Expert(nn.Module):
    """
    Ein einzelner Experte: eine gewoehnliche Zwei-Layer-FFN wie in TinyGPT.
    Wir halten das absichtlich identisch zur FFN in `GPTMini`, damit der
    Vergleich "dicht (TinyGPT) vs. spaerlich (TinyMoE)" ceteris paribus ist.
    """

    def __init__(self, embed_dim: int):
        super().__init__()
        self.fc1 = nn.Linear(embed_dim, 4 * embed_dim)
        self.fc2 = nn.Linear(4 * embed_dim, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(F.relu(self.fc1(x)))


class TopKGate(nn.Module):
    """
    Berechnet fuer jedes Token eine Verteilung ueber die Experten und
    waehlt die Top-k Experten.

    Rueckgabe:
      routing_weights: (B*T, K)     - Softmax-Gewichte der gewaehlten Experten
      expert_indices:  (B*T, K)     - Indices der gewaehlten Experten
      full_probs:      (B*T, N)     - vollstaendige Softmax-Verteilung
                                       (nur fuer den Load-Balancing-Loss)
    """

    def __init__(self, embed_dim: int, num_experts: int, top_k: int):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        self.gate = nn.Linear(embed_dim, num_experts, bias=False)

    def forward(self, x_flat: torch.Tensor):
        # x_flat: (B*T, D)
        logits = self.gate(x_flat)                # (B*T, N)
        full_probs = F.softmax(logits, dim=-1)    # (B*T, N)

        # Top-k
        top_vals, top_idx = torch.topk(full_probs, self.top_k, dim=-1)  # (B*T, K)

        # Renormalisieren: die K gewaehlten Gewichte sollen sich zu 1 summieren.
        # Ohne diesen Schritt haetten wir eine "Skalierung nach unten", weil die
        # Top-k Wahrscheinlichkeiten zusammen typisch << 1 ergeben.
        routing_weights = top_vals / (top_vals.sum(dim=-1, keepdim=True) + 1e-9)

        return routing_weights, top_idx, full_probs


def load_balancing_loss(
    full_probs: torch.Tensor,   # (B*T, N) - Softmax-Gewichte pro Token
    top_idx: torch.Tensor,      # (B*T, K) - gewaehlte Experten pro Token
    num_experts: int,
) -> torch.Tensor:
    """
    Load-Balancing-Loss aus Shazeer et al. 2017.

    Wir definieren zwei Groessen pro Experte i:

      f_i = Anteil der Tokens, die Experte i AUSGEWAEHLT haben (hart)
      P_i = mittlerer Routing-Wahrscheinlichkeitswert fuer Experte i (weich)

    Aux-Loss = N * sum_i (f_i * P_i)

    Interpretation:
      * Wenn alle Experten gleich haeufig gewaehlt werden, ist
        sum_i (f_i * P_i) = N * (1/N) * (1/N) = 1/N -> Loss = 1
      * Wenn *ein* Experte immer gewaehlt wird, wird f_j = 1, P_j nahe 1
        und alle anderen 0 -> Loss = N (schlecht!)

    Der Gradient dieses Loss wirkt NUR auf das Gating (durch P_i, das
    differenzierbar ist), nicht auf die harte Auswahl f_i (die durch
    top_k geht und keinen Gradient hat).
    """
    n_tokens = full_probs.size(0)

    # f_i: Zaehle, wie oft Experte i in top_idx auftaucht, normiere durch n_tokens.
    # (top_idx enthaelt pro Token K Indices; jeder Token traegt zu K Experten
    # eine "Wahl" bei -> Summe = n_tokens * K, aber wir teilen durch n_tokens
    # und lassen das K in der Konstanten unter.)
    #
    # torch.bincount waere natuerlicher, funktioniert aber nicht mit einem
    # 2D-Tensor - wir plaetten also.
    one_hot = F.one_hot(top_idx.reshape(-1), num_classes=num_experts).float()  # (n_tokens*K, N)
    fraction = one_hot.mean(dim=0)  # (N,)    Anteil der (Token,Rank)-Paare pro Experte

    # P_i: mittlere Routing-Wahrscheinlichkeit ueber alle Tokens
    routing_prob = full_probs.mean(dim=0)  # (N,)

    return num_experts * (fraction * routing_prob).sum()


class MoELayer(nn.Module):
    """
    Sparsely-Gated Mixture-of-Experts-Layer. Drop-in-Ersatz fuer die FFN in
    einem Transformer-Block.
    """

    def __init__(self, embed_dim: int, num_experts: int, top_k: int):
        super().__init__()
        assert top_k <= num_experts, "top_k > num_experts ist unsinnig"
        self.embed_dim = embed_dim
        self.num_experts = num_experts
        self.top_k = top_k
        self.gate = TopKGate(embed_dim, num_experts, top_k)
        self.experts = nn.ModuleList([Expert(embed_dim) for _ in range(num_experts)])

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x: (B, T, D)

        Rueckgabe:
          y:        (B, T, D)  - die MoE-Ausgabe
          aux_loss: skalar     - Load-Balancing-Loss dieser Schicht
        """
        B, T, D = x.shape
        x_flat = x.reshape(B * T, D)  # jeder Token wird unabhaengig geroutet

        routing_weights, top_idx, full_probs = self.gate(x_flat)
        # routing_weights: (B*T, K)
        # top_idx:         (B*T, K)
        # full_probs:      (B*T, N)

        # Wir gehen die Experten der Reihe nach durch. Fuer jeden Experten
        # sammeln wir die Tokens ein, fuer die er zu den Top-k gehoert, jagen
        # sie durch den Experten und schreiben die gewichtete Ausgabe zurueck.
        # Das ist die naive, aber didaktisch klare Umsetzung. Produktions-
        # Frameworks nutzen dispatch/combine-Kernels; die Idee ist identisch.
        y_flat = torch.zeros_like(x_flat)
        for e_id, expert in enumerate(self.experts):
            # Fuer welche Tokens ist Experte e_id unter den Top-k? Suche
            # `e_id` in jeder Zeile von top_idx.
            # match: (B*T, K) bool - True an den (token, rank)-Positionen,
            # an denen dieser Experte gewaehlt wurde.
            match = (top_idx == e_id)
            if not match.any():
                continue  # Experte wurde in diesem Batch nicht gewaehlt

            # Fuer jedes ausgewaehlte Paar (token_id, rank):
            #   - hole den Token-Vektor x_flat[token_id]
            #   - hole das zugehoerige Routing-Gewicht routing_weights[token_id, rank]
            # `.nonzero()` liefert eine Liste von (token_id, rank)-Paaren.
            token_ids, ranks = match.nonzero(as_tuple=True)
            expert_input = x_flat[token_ids]                              # (n_sel, D)
            weights = routing_weights[token_ids, ranks].unsqueeze(-1)     # (n_sel, 1)

            expert_output = expert(expert_input) * weights                # (n_sel, D)

            # Zurueck-Aggregation: dasselbe Token kann mehrere Experten gewaehlt
            # haben, deren gewichtete Outputs sollen sich addieren.
            # `index_add_` macht genau das - auch mit doppelten token_ids.
            y_flat.index_add_(0, token_ids, expert_output)

        aux_loss = load_balancing_loss(full_probs, top_idx, self.num_experts)
        return y_flat.reshape(B, T, D), aux_loss
