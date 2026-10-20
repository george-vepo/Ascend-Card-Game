"""Ponte experimental para simulação em segundo plano (issue #35).

Uma IA pode ESCOLHER ações de seu controlador e propor sua interpretação,
mas nunca altera o estado nem autoriza dados. O executor fechado invoca
somente comandos SRD JÁ implementados no MotorRoperBasico.

Este módulo não executa modelo, não cria thread nem jogo oficial. Um worker
externo pode agendar `processar_passo`/`processar_lote` desacoplados da UI.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from motor_poc import digest
from motor_roper_basico import SessaoRoperFixture


ACTIONS = {
    "ATAQUE_ROPER_BASICO_TESTE": (
        frozenset({"aceite_escopo", "ataque"}),
        frozenset({"d20_simulado", "d20_simulados", "dano_dados",
                   "d20_concentracao_simulado"}),
    ),
    "TENTACLE_ROPER_TESTE": (
        frozenset({"aceite_escopo", "tentaculo_numero"}),
        frozenset({"d20_simulado"}),
    ),
    "ESCAPAR_GRAPPLE_ROPER_TESTE": (
        frozenset({"aceite_escopo", "pericia"}),
        frozenset({"d20_simulados"}),
    ),
    "REEL_ROPER_TESTE": (frozenset(), frozenset()),
    "CONJURAR_MAGIA_OWL_TESTE": (
        frozenset({"aceite_escopo", "magia"}),
        frozenset(),
    ),
    "ENCERRAR_CONCENTRACAO_OWL_TESTE": (frozenset(), frozenset()),
}
PROPOSTA_KEYS = frozenset({
    "contrato", "evento_id", "ator", "comando", "fase",
    "versao_estado", "hash_estado", "fonte_copia_id",
    "fonte_sha256", "opcoes", "justificativa",
})
DECLARACAO_KEYS = frozenset({
    "evento_id", "ator", "comando", "opcoes", "origem",
})
DADOS_KEYS = frozenset({"evento_id", "origem", "dados"})
FINAL = frozenset({"CONCLUIDO", "FALHOU"})
ESTADOS = frozenset({
    "NA_FILA", "EXECUTANDO", "AGUARDANDO_JOGADOR", "AGUARDANDO_DADOS",
    "PENDENTE_REGRA", "CONCLUIDO", "FALHOU",
})


def _validate_exact(value: Any, keys: frozenset, label: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label}: campos obrigatórios/permitidos divergentes")


def contexto_publico(sessao: SessaoRoperFixture) -> dict:
    """Somente projeção pública + compromisso hash, sem mãos nem ordem do monte."""
    motor = sessao.motor
    mesa = motor.public()
    ator = mesa.get("ator_da_vez")
    fonte = None
    if ator in ("J1", "J2"):
        j = motor.state["jogadores"][ator]
        cid = j.get("criatura_ativa_id")
        if cid:
            card = j["cartas"][cid]
            origem = card.get("origem_ficha")
            if not origem or not origem.get("sha256_documento"):
                raise ValueError("ficha ativa sem proveniência canônica")
            fonte = {
                "copia_id": cid,
                "sha256_documento": origem["sha256_documento"],
            }
    return {
        "contrato": "ARBITRO_IA_BACKGROUND_V1",
        "ambiente": "FIXTURE_ISOLADA_NAO_OFICIAL",
        "mesa": mesa,
        "versao_estado": motor.state["versao"],
        "hash_estado": digest(motor.state),
        "fonte_ator": fonte,
        "sem_posicionamento": True,
    }


@dataclass
class JobSimulacao:
    job_id: str
    sessao: SessaoRoperFixture
    max_passos: int = 64
    estado: str = "NA_FILA"
    realizados: int = 0
    observacoes_publicas: list[dict] = field(default_factory=list)
    _respostas: dict[str, dict] = field(default_factory=dict, repr=False)
    _fingerprints: dict[str, str] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        if (not isinstance(self.job_id, str) or not self.job_id.strip()
                or type(self.max_passos) is not int or not 1 <= self.max_passos <= 1000):
            raise ValueError("job_id ou limite de passos inválidos")
        if not isinstance(self.sessao, SessaoRoperFixture):
            raise ValueError("somente fixture Roper/Owl nesta primeira entrega")
        if self.sessao.motor.state["fase"] != "COMBATE":
            raise ValueError("job só pode começar após entrada na fase de combate")

    def status_publico(self) -> dict:
        mesa = self.sessao.mesa_publica()
        return copy.deepcopy({
            "job_id": self.job_id,
            "estado": self.estado,
            "passos_aceitos": self.realizados,
            "limite_passos": self.max_passos,
            "partida": "FIXTURE_ISOLADA_NAO_OFICIAL",
            "versao_estado": self.sessao.motor.state["versao"],
            "fase": mesa["fase"],
            "ator_da_vez": mesa["ator_da_vez"],
            "placar_fixture": mesa["placar"],
            "historico_publico": self.observacoes_publicas,
        })

    def processar_passo(self, declaracao: dict | None,
                        proposta: dict | None, rolagens: dict | None) -> dict:
        """Avança no máximo UM evento; se exigir pessoa/dados, suspende sem mutar."""
        if self.estado in FINAL:
            return self.status_publico()
        if self.sessao.motor.state["fase"] != "COMBATE":
            self.estado = "CONCLUIDO"
            return self.status_publico()
        if self.realizados >= self.max_passos:
            self.estado = "PENDENTE_REGRA"
            return self.status_publico()
        actor = self.sessao.motor.state["ator_da_vez"]
        if declaracao is None or proposta is None:
            self.estado = "AGUARDANDO_JOGADOR" if actor == "J1" else "NA_FILA"
            return self.status_publico()
        self.estado = "EXECUTANDO"
        try:
            _validate_exact(declaracao, DECLARACAO_KEYS, "declaração")
            _validate_exact(proposta, PROPOSTA_KEYS, "proposta")
            if not isinstance(declaracao["evento_id"], str) or not declaracao["evento_id"]:
                raise ValueError("ID do evento ausente")
            eid = declaracao["evento_id"]
            # Primeiro verifica replay: a base já pode ter avançado depois
            # da aplicação original; não exigir a versão/ator antigo novamente.
            if rolagens is not None:
                fp_replay = digest({
                    "decl": declaracao, "proposta": proposta, "rolagens": rolagens
                })
                if eid in self._fingerprints:
                    if self._fingerprints[eid] != fp_replay:
                        raise ValueError("colisão de evento/idempotência")
                    return copy.deepcopy(self._respostas[eid])
            if not isinstance(declaracao["opcoes"], dict):
                raise ValueError("opções de declaração inválidas")
            if declaracao["ator"] != actor:
                raise ValueError("ator não coincide com a vez")
            if (declaracao["origem"] != (
                    "HUMANO_AUTENTICADO" if actor == "J1" else "IA_CONTROLADORA"
            )):
                raise ValueError("autoria de declaração incompatível com controlador")
            command = declaracao["comando"]
            if command not in ACTIONS:
                raise ValueError("comando fora da lista fechada")
            choice_fields, dice_fields = ACTIONS[command]
            if not set(declaracao["opcoes"]) <= choice_fields:
                raise ValueError("declaração não pode fornecer rolagens nem efeito")
            context = contexto_publico(self.sessao)
            source = context["fonte_ator"]
            if not source:
                raise ValueError("criatura ativa sem ficha")
            expected = {
                "contrato": "ARBITRO_IA_BACKGROUND_V1",
                "evento_id": eid,
                "ator": actor,
                "comando": command,
                "fase": context["mesa"]["fase"],
                "versao_estado": context["versao_estado"],
                "hash_estado": context["hash_estado"],
                "fonte_copia_id": source["copia_id"],
                "fonte_sha256": source["sha256_documento"],
                "opcoes": declaracao["opcoes"],
            }
            if any(proposta.get(k) != v for k, v in expected.items()):
                raise ValueError("proposta diverge da declaração/estado/fonte")
            if (not isinstance(proposta["justificativa"], str)
                    or not proposta["justificativa"].strip()
                    or len(proposta["justificativa"]) > 2000):
                raise ValueError("fundamentação ausente/inválida")
            if rolagens is None:
                self.estado = "AGUARDANDO_DADOS"
                return self.status_publico()
            _validate_exact(rolagens, DADOS_KEYS, "pacote de rolagens")
            if (rolagens["evento_id"] != eid or
                    rolagens["origem"] != "SIMULADO_EXTERNO_TESTE"):
                raise ValueError("dados sem origem externa da fixture comprovada")
            if (not isinstance(rolagens["dados"], dict)
                    or not set(rolagens["dados"]) <= dice_fields):
                raise ValueError("rolagens com chaves fora da autorização")
            params = {**declaracao["opcoes"], **rolagens["dados"]}
            fp = digest({"decl": declaracao, "proposta": proposta, "rolagens": rolagens})
            # Não aceitar um evento repetido que exista no motor, mas não no job.
            if eid in self.sessao.motor.responses:
                raise ValueError("evento já registrado fora deste job")
            resultado = self.sessao.comando(eid, actor, command, params)
            self._fingerprints[eid] = fp
            if resultado["decisao"] == "ACEITA":
                self.realizados += 1
                self.observacoes_publicas.append({
                    "evento_id": eid, "ator": actor, "acao": command,
                    "decisao": "ACEITA", "versao": resultado["versao"],
                    "placar_fixture": copy.deepcopy(self.sessao.motor.state["placar"]),
                })
                if self.sessao.motor.state["fase"] != "COMBATE":
                    self.estado = "CONCLUIDO"
                elif self.realizados >= self.max_passos:
                    self.estado = "PENDENTE_REGRA"
                elif self.sessao.motor.state["ator_da_vez"] == "J1":
                    self.estado = "AGUARDANDO_JOGADOR"
                else:
                    self.estado = "NA_FILA"  # próximo passo em outro tick do worker
            elif resultado["decisao"] == "PENDENTE":
                motivo = resultado.get("motivo", "").casefold()
                self.estado = (
                    "AGUARDANDO_DADOS" if any(
                        word in motivo for word in ("d20", "rolag", "dados ")
                    ) else "PENDENTE_REGRA"
                )
            else:
                self.estado = "FALHOU"
            public_result = self.status_publico()
            public_result["decisao_ultimo_passo"] = resultado["decisao"]
            self._respostas[eid] = copy.deepcopy(public_result)
            return public_result
        except (TypeError, KeyError, ValueError) as exc:
            self.estado = "FALHOU"
            outcome = self.status_publico()
            outcome["erro"] = str(exc)
            return outcome

    def processar_lote(self, passos: list[tuple[dict, dict, dict]],
                       *, limite_por_lote: int = 8) -> dict:
        """Ponto de integração do worker desacoplado; nunca faz loop infinito."""
        if (type(limite_por_lote) is not int
                or not 1 <= limite_por_lote <= 32
                or not isinstance(passos, list)):
            raise ValueError("lote inválido")
        for step in passos[:limite_por_lote]:
            if self.estado in FINAL or self.estado == "PENDENTE_REGRA":
                break
            if not isinstance(step, tuple) or len(step) != 3:
                raise ValueError("passo deve conter declaração/proposta/dados")
            self.processar_passo(*step)
            if self.estado in FINAL or self.estado in {
                    "PENDENTE_REGRA", "AGUARDANDO_DADOS"}:
                break
        return self.status_publico()
