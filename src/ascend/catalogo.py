"""Leitor local do repositório Catálogo SRD, sem copiar dados para o Ascend.

Este adaptador NÃO homologa fichas ou traduz campos em ataques/habilidades de jogo.
O chamador deve validar as estruturas e a revisão (commit) de origem.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CatalogoIndisponivel(RuntimeError):
    """O checkout externo do Catálogo SRD não foi encontrado."""


class CatalogoSRD:
    CAMINHOS = {
        "megalista": "docs/catalogo/data/megalista-1320.json",
        "fichas": "docs/catalogo/data/fichas-607.json",
        "deck_celestial": "docs/catalogo/data/deck-celestial-40.json",
        "deck_aberracao": "docs/catalogo/data/deck-aberracao-40.json",
    }

    def __init__(self, repositorio: str | Path):
        self.raiz = Path(repositorio).expanduser().resolve()

    def ler_json(self, nome: str) -> Any:
        if nome not in self.CAMINHOS:
            raise ValueError("Recurso de catálogo não autorizado: " + str(nome))
        caminho = (self.raiz / self.CAMINHOS[nome]).resolve()
        if not caminho.is_relative_to(self.raiz):
            raise ValueError("Caminho externo ao catálogo")
        try:
            return json.loads(caminho.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise CatalogoIndisponivel(
                f"Arquivo indisponível: {self.CAMINHOS[nome]}. "
                "Forneça um checkout externo atualizado do Catálogo SRD."
            ) from exc
