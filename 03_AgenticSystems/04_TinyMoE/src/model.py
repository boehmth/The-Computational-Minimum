"""
model.py - GPTMiniMoE: TinyGPT-Architektur mit MoE statt dichter FFN

Der einzige Unterschied zu `GPTMini` aus Kap. 3.1 ist, dass der FFN-Block
in jedem Decoder-Layer durch eine `MoELayer` ersetzt ist. Alles andere -
Embeddings, Attention, LayerNorm, Output-Head - ist identisch.

Das ist der zentrale didaktische Punkt: MoE ist eine *lokale* Aenderung,
kein neuer Architektur-Familientyp. Der ganze Rest des Transformers
funktioniert wie gehabt.
"""

from __future__ import annotations

from typing import List, Tuple

import torch
import torch.nn as nn

from moe_layer import MoELayer


class MoEDecoderBlock(nn.Module):
    """
    Ein Decoder-Block wie in TinyGPT, aber mit MoE-Feed-Forward.

    Vergleich zu `DecoderBlock` in `01_TinyGPT/src/tinyGPT.py`:

        DecoderBlock:                        MoEDecoderBlock:
            self.ff = nn.Sequential(...)    self.ff = MoELayer(...)   <-- Unterschied

    Beide Bloecke haben dieselbe Signatur:
        forward(x, key_padding_mask=None) -> x
    - nur dass MoEDecoderBlock zusaetzlich einen aux_loss zurueckgibt, der
      im GPTMiniMoE aufsummiert wird.
    """

    def __init__(self, embed_dim: int, n_heads: int, num_experts: int, top_k: int):
        super().__init__()
        self.attn = nn.MultiheadAttention(embed_dim, n_heads, batch_first=True)
        self.ln1 = nn.LayerNorm(embed_dim)
        self.ff = MoELayer(embed_dim, num_experts=num_experts, top_k=top_k)
        self.ln2 = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor, key_padding_mask=None) -> Tuple[torch.Tensor, torch.Tensor]:
        T = x.size(1)
        causal_mask = torch.triu(torch.ones(T, T, device=x.device) * float('-inf'), 1)
        attn_out, _ = self.attn(
            x, x, x,
            attn_mask=causal_mask,
            key_padding_mask=key_padding_mask,
        )
        x = self.ln1(x + attn_out)

        ff_out, aux_loss = self.ff(x)  # <-- der einzige echte Unterschied
        x = self.ln2(x + ff_out)
        return x, aux_loss


class GPTMiniMoE(nn.Module):
    """
    MoE-Variante von GPTMini (Kap. 3.1). API-kompatibel: forward gibt
    logits zurueck (wie GPTMini), zusaetzlich einen `last_aux_loss`
    Attribut fuer den Trainings-Loop.

    Warum kein Rueckgabewert `(logits, aux_loss)`? Weil das mit den
    Standard-Test/Eval-Skripten aus 3.1/3.2/3.3 nicht mehr kompatibel
    waere. Wir bevorzugen die minimale API-Aenderung.
    """

    def __init__(
        self,
        vocab_size: int,
        context_length: int,
        embed_dim: int,
        n_heads: int,
        n_layers: int,
        num_experts: int,
        top_k: int,
    ):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(context_length, embed_dim)
        self.blocks = nn.ModuleList([
            MoEDecoderBlock(embed_dim, n_heads, num_experts, top_k)
            for _ in range(n_layers)
        ])
        self.ln_final = nn.LayerNorm(embed_dim)
        self.output_head = nn.Linear(embed_dim, vocab_size)

        # Wird pro Forward-Pass gefuellt; der Trainings-Loop liest es aus.
        self.last_aux_loss: torch.Tensor = torch.tensor(0.0)

    def forward(self, x: torch.Tensor, attention_mask=None) -> torch.Tensor:
        B, T = x.size()
        tok = self.token_embedding(x)
        pos = self.position_embedding(torch.arange(T, device=x.device).unsqueeze(0))
        h = tok + pos

        key_padding_mask = None
        if attention_mask is not None:
            key_padding_mask = attention_mask == 0

        aux_losses: List[torch.Tensor] = []
        for block in self.blocks:
            h, aux = block(h, key_padding_mask=key_padding_mask)
            aux_losses.append(aux)

        h = self.ln_final(h)

        # Ueber alle Layer mitteln: jeder MoE-Layer traegt gleich viel bei.
        # In der Praxis wird das oft auch einfach aufsummiert - unser Ergebnis
        # ist ohnehin identisch bis auf einen konstanten Faktor, den man ueber
        # LOAD_BALANCE_WEIGHT im config.json kompensieren kann.
        if aux_losses:
            self.last_aux_loss = torch.stack(aux_losses).mean()
        else:
            self.last_aux_loss = torch.tensor(0.0, device=h.device)

        return self.output_head(h)