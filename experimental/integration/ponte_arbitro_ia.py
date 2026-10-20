"""Ponte experimental IA -> motor determinístico; NUNCA árbitro de produção.

Não chama modelo, não gera rolagens, não expõe dados ocultos e não aceita
patches de estado escritos pela IA. Admite SOMENTE comandos já implementados
no motor Roper × Giant Owl (fixture de testes).
"""
from __future__ import annotations

import copy
import json
from typing import Any, Mapping

from motor_poc import digest
from motor_roper_basico import (
    ESCOPO_BASICO, ESCOPO_CONJURACAO_OWL,
)

SCHEMA_CONTEXTO = "ASCEND_IA_CONTEXTO_PUBLICO_V1"
SCHEMA_PROPOSTA = "ASCEND_IA_PROPOSTA_V1"
FONTE_CATALOGO = "03f84e8426f469ef6a0e471faea2093b7c0b69c9"

# Os campos de escolha vêm da DECLARAÇÃO autenticada do jogador, NÃO da IA.
# Os dados são recebidos de fonte EXTERNA ao modelo, nunca de suas respostas.
ACOES = {
    "ATAQUE_ROPER_BASICO_TESTE": (
        {"ataque"}, {"d20_simulado", "d20_simulados",
                     "dano_dados", "d20_concentracao_simulado"},
        ESCOPO_BASICO,
    ),
    "TENTACLE_ROPER_TESTE": (
        {"tentaculo_numero"}, {"d20_simulado"}, ESCOPO_BASICO,
    ),
    "ESCAPAR_GRAPPLE_ROPER_TESTE": (
        {"pericia"}, {"d20_simulados"}, ESCOPO_BASICO,
    ),
    "ATACAR_TENTACULO_ROPER_TESTE": (
        {"tentaculo_numero", "ataque"}, {"d20_simulados", "dano_dados"},
        ESCOPO_BASICO,
    ),
    "REEL_ROPER_TESTE": (set(), set(), None),
    "CONJURAR_MAGIA_OWL_TESTE": (
        {"magia"}, set(), ESCOPO_CONJURACAO_OWL,
    ),
    "ENCERRAR_CONCENTRACAO_OWL_TESTE": (set(), set(), None),
}
# Multiattack exige uma interface de rolagens encadeadas e não é aceito
# por esta ponte V1, embora já exista no motor manual do Roper.


class PonteArbitroIA:
    """A IA nunca recebe sessão interna nem acesso a escrita direta no motor."""

    def __init__(self, sessao):
        self._sessao = sessao

    def contexto_publico(self) -> dict:
        """Somente projeção pública já existente, sem cards de mão/deck."""
        motor = self._sessao.motor
        mesa = copy.deepcopy(self._sessao.mesa_publica())
        return {
            "schema": SCHEMA_CONTEXTO,
            "ambiente": "FIXTURE_ISOLADA_NAO_OFICIAL",
            "partida_id": mesa["partida_id"],
            "versao_estado": motor.state["versao"],
            "fase": mesa["fase"],
            "ator_da_vez": mesa["ator_da_vez"],
            "mesa": mesa,
            "catalogo_pin": FONTE_CATALOGO,
            "acoes_v1": sorted(ACOES),
            "integridade_publica_sha256": digest({
                "mesa": mesa, "versao": motor.state["versao"],
            }),
        }

    def _recusar(self, decisao: str, motivo: str) -> dict:
        return {
            "decisao": decisao,
            "motivo": motivo,
            "versao": self._sessao.motor.state["versao"],
            "estado_alterado": False,
        }

    def processar(
        self, *, jogador_autenticado: str, declaracao: Mapping[str, Any],
        proposta_ia: Mapping[str, Any], dados_arbitro: Mapping[str, Any],
        evento_id: str,
    ) -> dict:
        """Somente declaração assinada pelo controlador pode virar comando.

        A proposta é **não confiável**: qualquer diferença da declaração
        bloqueia o processamento. Regras/dados são novamente validados pelo
        motor transacional; a IA não pode escolher um resultado ou editar PV.
        """
        if jogador_autenticado not in ("J1", "J2"):
            return self._recusar("REJEITADA", "identidade de jogador não autenticada")
        if not isinstance(evento_id, str) or not 1 <= len(evento_id) <= 100:
            return self._recusar("REJEITADA", "identificador de evento inválido")
        if not all(isinstance(x, Mapping)
                   for x in (declaracao, proposta_ia, dados_arbitro)):
            return self._recusar("REJEITADA", "contrato de mensagem inválido")
        if set(declaracao) != {"jogador", "acao", "opcoes"}:
            return self._recusar("REJEITADA", "declaração fora do contrato")
        if set(proposta_ia) != {
            "schema", "partida_id", "versao_estado", "contexto_hash",
            "fase", "jogador", "acao", "opcoes", "justificativa", "fonte",
        }:
            return self._recusar("REJEITADA", "proposta IA contém campos desconhecidos")
        if (proposta_ia["schema"] != SCHEMA_PROPOSTA
                or proposta_ia["fonte"] != "SRD 5.2.1"
                or type(proposta_ia["justificativa"]) is not str
                or not 1 <= len(proposta_ia["justificativa"]) <= 1000):
            return self._recusar("REJEITADA", "fonte ou justificativa da IA inválida")
        if (declaracao["jogador"] != jogador_autenticado
                or proposta_ia["jogador"] != jogador_autenticado
                or proposta_ia["acao"] != declaracao["acao"]
                or proposta_ia["opcoes"] != declaracao["opcoes"]):
            return self._recusar("REJEITADA", "IA tentou alterar a escolha autenticada")
        acao = declaracao["acao"]
        if not isinstance(acao, str) or acao not in ACOES:
            return self._recusar(
                "PENDENTE", "ação fora da ponte V1: requer motor ou regra verificável"
            )
        opcoes, campos_dados, escopo = ACOES[acao]
        if (not isinstance(declaracao["opcoes"], dict)
                or set(declaracao["opcoes"]) != opcoes):
            return self._recusar("REJEITADA", "opções da ação fora do contrato")
        if (set(dados_arbitro) != {"origem", "valores"}
                or dados_arbitro["origem"] != "DADOS_SIMULADOS_TESTE"
                or not isinstance(dados_arbitro["valores"], dict)
                or not set(dados_arbitro["valores"]).issubset(campos_dados)):
            return self._recusar(
                "REJEITADA", "dados devem vir do árbitro externo ao modelo"
            )
        if (len(json.dumps(declaracao, ensure_ascii=False)) > 2000
                or len(json.dumps(dados_arbitro, ensure_ascii=False)) > 4000):
            return self._recusar("REJEITADA", "payload excessivo")
        params = {
            **copy.deepcopy(declaracao["opcoes"]),
            **copy.deepcopy(dados_arbitro["valores"]),
        }
        if escopo:
            params["aceite_escopo"] = escopo
        # Prova de origem armazenada no evento existente, nunca um patch da IA.
        params["comprovante_ponte_ia"] = {
            "schema": SCHEMA_PROPOSTA,
            "hash_proposta": digest(dict(proposta_ia)),
            "hash_declaracao": digest(dict(declaracao)),
            "hash_contexto": proposta_ia["contexto_hash"],
            "fonte_dados": "DADOS_SIMULADOS_TESTE",
        }
        motor = self._sessao.motor
        fingerprint = digest({
            "evento_id": evento_id, "autor": jogador_autenticado,
            "acao": acao, "parametros": params,
        })
        previous = motor.responses.get(evento_id)
        if previous:
            if previous["fingerprint"] != fingerprint:
                return self._recusar(
                    "REJEITADA", "colisão de evento com proposta diferente"
                )
            return copy.deepcopy(previous["result"])

        current = self.contexto_publico()
        if (proposta_ia["partida_id"] != current["partida_id"]
                or proposta_ia["versao_estado"] != current["versao_estado"]
                or proposta_ia["contexto_hash"] != current["integridade_publica_sha256"]
                or proposta_ia["fase"] != current["fase"]):
            return self._recusar(
                "PENDENTE", "contexto obsoleto ou divergente: pedir novo parecer"
            )
        if current["fase"] != "COMBATE":
            return self._recusar("REJEITADA", "fora da fase de combate")
        if (acao != "ENCERRAR_CONCENTRACAO_OWL_TESTE"
                and current["ator_da_vez"] != jogador_autenticado):
            return self._recusar("REJEITADA", "jogador fora da vez")
        # ÚNICO ponto de escrita autorizado: API transacional preexistente.
        return self._sessao.comando(evento_id, jogador_autenticado, acao, params)
