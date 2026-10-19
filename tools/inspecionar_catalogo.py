"""Audita identidades públicas do catálogo; não toca estado de partida."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from ascend.catalogo_poc import carregar_referencias, ler_contrato


def main() -> int:
    p = argparse.ArgumentParser(description="Verificar decks de referência do Catálogo SRD")
    p.add_argument("--catalogo", required=True, help="Caminho do checkout Catálogo SRD")
    args = p.parse_args()
    cartas, meta = carregar_referencias(args.catalogo, ler_contrato(RAIZ))
    resultado = {
        "fonte": meta["repositor_io"],
        "commit": meta["revisao_git"],
        "revisao_verificada": meta["revisao_verificada"],
        "copias": meta["copias"],
        "raridades": {
            j: dict(Counter(c.raridade for c in cartas if c.jogador == j))
            for j in ("J1", "J2")
        },
        "dados_homologados_automaticamente": False,
        "partida_oficial_modificada": False,
        "sha256_conteudos": meta["sha256_conteudos"],
    }
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
