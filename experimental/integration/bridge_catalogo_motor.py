"""Ponte experimental SOMENTE entre identidades do Catálogo SRD e motor legado.

As 80 cópias são carregadas por referência; atributos e habilidades não são
inventados, nem copiados para o Ascend. O motor só funciona em fixtures
isoladas. Nenhuma API aqui inicia uma partida oficial ou realiza sorteios.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ascend.catalogo_poc import CopiaReferencia, carregar_referencias
from motor_poc import (
    MotorPOC,
    CorruptedCheckpoint,
    InvalidAction,
    digest,
)


class FonteDivergente(CorruptedCheckpoint):
    """A origem ou as identidades foram alteradas desde o checkpoint."""


def _registros(
    referencias: Sequence[CopiaReferencia],
    pv_simulados: Mapping[str, int] | None = None,
) -> list[dict[str, Any]]:
    """Transfere SOMENTE identidade/cópia; PV apenas de fixture explicitada."""
    if len(referencias) != 80:
        raise InvalidAction("fixture exige 80 cópias de referência")
    ids = [c.id_copia for c in referencias]
    if len(set(ids)) != 80:
        raise InvalidAction("IDs de cópia duplicados")
    for lado, prefixo in (("J1", "CE"), ("J2", "AB-POC")):
        subset = [c for c in referencias if c.jogador == lado]
        if len(subset) != 40:
            raise InvalidAction(f"{lado} exige exatamente 40 cópias")
        for i, c in enumerate(subset, 1):
            if c.id_copia != f"{prefixo}-{i:03d}" or c.posicao_referencia != i:
                raise InvalidAction(f"IDs/posições inconsistentes em {lado}")

    dados_pv = dict(pv_simulados or {})
    if set(dados_pv) - set(ids):
        raise InvalidAction("PV de fixture para cópia inexistente")
    if any(type(v) is not int or v < 1 for v in dados_pv.values()):
        raise InvalidAction("PV de fixture devem ser inteiros positivos")
    return [
        {
            "jogador": c.jogador,
            "id_copia_poc": c.id_copia,
            "chave_controle_1320": c.id_catalogo,
            "nome": c.nome,
            "tipo": c.tipo,
            "nd": str(c.nd),
            "raridade": c.raridade,
            "pv_fonte": dados_pv.get(c.id_copia),
        }
        for c in referencias
    ]


@dataclass
class SessaoFixture:
    """Referências + contrato de origem + motor legado em memória, não oficial."""

    motor: MotorPOC
    registros: list[dict[str, Any]]
    proveniencia: dict[str, Any]
    hash_identidades: str

    @classmethod
    def de_referencias(
        cls,
        referencias: Sequence[CopiaReferencia],
        proveniencia: Mapping[str, Any],
        *,
        primeiro: str = "J1",
        maos_fixadas: dict[str, list[str]] | None = None,
        pv_simulados: Mapping[str, int] | None = None,
    ) -> "SessaoFixture":
        """Somente para teste; a origem já deve ter sido conferida pelo leitor."""
        registros = _registros(referencias, pv_simulados)
        if not isinstance(proveniencia, Mapping) or not isinstance(
            proveniencia.get("sha256_conteudos"), dict
        ):
            raise InvalidAction("proveniência dos dois arquivos obrigatória")
        if set(proveniencia["sha256_conteudos"]) != {"celestial", "aberracao"}:
            raise InvalidAction("dois hashes de origem obrigatórios")
        motor = MotorPOC(
            registros,
            first=primeiro,
            hands=maos_fixadas,
            match_id="ASCEND-FIXTURE-NAO-OFICIAL",
            test_fixture=True,
        )
        return cls(
            motor=motor,
            registros=copy.deepcopy(registros),
            proveniencia=copy.deepcopy(dict(proveniencia)),
            hash_identidades=digest(registros),
        )

    @classmethod
    def de_checkout(
        cls,
        checkout_catalogo: str,
        contrato: dict[str, Any],
        *,
        primeiro: str = "J1",
        maos_fixadas: dict[str, list[str]] | None = None,
        pv_simulados: Mapping[str, int] | None = None,
    ) -> "SessaoFixture":
        """Exige commit do Catálogo SRD fixado no contrato; nenhuma escrita."""
        referencias, proveniencia = carregar_referencias(
            checkout_catalogo, contrato, exigir_revisao=True
        )
        return cls.de_referencias(
            referencias,
            proveniencia,
            primeiro=primeiro,
            maos_fixadas=maos_fixadas,
            pv_simulados=pv_simulados,
        )

    def comando(self, evento_id: str, ator: str, acao: str, params=None) -> dict:
        return self.motor.apply(evento_id, ator, acao, params)

    def mesa_publica(self) -> dict:
        return self.motor.public()

    def visao_privada(self, jogador: str) -> dict:
        return self.motor.private(jogador)

    def checkpoint(self) -> dict:
        """Não publicar: contém mãos, montes e dados internos da fixture."""
        return {
            "schema": "ASCEND_BRIDGE_FIXTURE_V1",
            "unicamente_teste": True,
            "proveniencia": copy.deepcopy(self.proveniencia),
            "hash_identidades": self.hash_identidades,
            "motor": self.motor.checkpoint(),
        }

    @classmethod
    def restaurar(
        cls,
        checkpoint: dict,
        referencias: Sequence[CopiaReferencia],
        proveniencia: Mapping[str, Any],
        *,
        pv_simulados: Mapping[str, int] | None = None,
    ) -> "SessaoFixture":
        if checkpoint.get("schema") != "ASCEND_BRIDGE_FIXTURE_V1" or (
            checkpoint.get("unicamente_teste") is not True
        ):
            raise FonteDivergente("checkpoint incompatível/não experimental")
        registros = _registros(referencias, pv_simulados)
        if (
            checkpoint.get("hash_identidades") != digest(registros)
            or checkpoint.get("proveniencia") != dict(proveniencia)
        ):
            raise FonteDivergente("cópias ou revisão do catálogo divergentes")
        motor = MotorPOC.restore(checkpoint["motor"], registros)
        return cls(
            motor=motor,
            registros=copy.deepcopy(registros),
            proveniencia=copy.deepcopy(dict(proveniencia)),
            hash_identidades=digest(registros),
        )
