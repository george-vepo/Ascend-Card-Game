"""Contrato de propostas da IA e simulação de combate em passos desacoplados.

Fixtures concretas, NÃO uma invocação real de modelo/sorteador. Fonte externa
pinada e dados simulados rotulados. Nunca inicia ou altera partida oficial.
"""
import copy
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for rel in ("src", "experimental/legacy/src", "experimental/integration"):
    sys.path.insert(0, str(ROOT / rel))

from ascend.catalogo_poc import ler_contrato
from motor_roper_basico import SessaoRoperFixture, ESCOPO_BASICO, ESCOPO_CONJURACAO_OWL
from arbitro_ia_background import (
    ACTIONS, JobSimulacao, contexto_publico,
)


class BackgroundArbiterSafety(unittest.TestCase):
    def setUp(self):
        self.source = os.environ["CATALOGO_SRD_DIR"]
        self.contract = ler_contrato(ROOT)
        self.sessao = SessaoRoperFixture.criar_de_checkout(
            self.source, self.contract, primeiro="J2",
            maos_fixadas={
                "J1": ["CE-001", "CE-002", "CE-003", "CE-004", "CE-005"],
                "J2": ["AB-POC-017", "AB-POC-001", "AB-POC-002",
                       "AB-POC-003", "AB-POC-004"],
            },
        )
        self.i = 0
        for p in ("J2", "J1"):
            self.ok(p, "TROCAR", {"descartar": []})
        for p, cid in (("J2", "AB-POC-017"), ("J1", "CE-001")):
            self.ok(p, "INVOCAR", {"carta_id": cid})
            self.ok(p, "PRONTO_CRIATURA")
        for p in ("J2", "J1"):
            self.ok(p, "ESCOLHER_SUPORTE", {"carta_id": None})
        for _ in range(2):
            self.ok("ARBITRO", "RESOLVER_SUPORTE_FIXTURE",
                    {"resultado": "PULAR"})
        self.ok("ARBITRO", "INICIATIVA_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "d20_simulados": {"J1": 1, "J2": 12},
        })
        self.assertEqual(self.sessao.motor.state["ator_da_vez"], "J2")
        self.job = JobSimulacao("simulacao-teste", self.sessao)

    def ok(self, actor, command, params=None):
        self.i += 1
        out = self.sessao.comando(
            f"prepare-background-{self.i}", actor, command, params or {}
        )
        self.assertEqual(out["decisao"], "ACEITA", out)
        return out

    def get_package(self, command="ATAQUE_ROPER_BASICO_TESTE",
                    options=None, dice=None, eid=None):
        context = contexto_publico(self.sessao)
        actor = context["mesa"]["ator_da_vez"]
        options = options if options is not None else {
            "aceite_escopo": ESCOPO_BASICO,
            "ataque": "Bite" if actor == "J2" else "Talons",
        }
        dice = dice if dice is not None else {
            "d20_simulado": 1,
            "dano_dados": [],
        }
        eid = eid or "ia-background-" + str(self.i + 1)
        declaration = {
            "evento_id": eid, "ator": actor, "comando": command,
            "opcoes": options,
            "origem": "HUMANO_AUTENTICADO" if actor == "J1"
                      else "IA_CONTROLADORA",
        }
        proposal = {
            "contrato": context["contrato"],
            "evento_id": eid,
            "ator": actor,
            "comando": command,
            "fase": context["mesa"]["fase"],
            "versao_estado": context["versao_estado"],
            "hash_estado": context["hash_estado"],
            "fonte_copia_id": context["fonte_ator"]["copia_id"],
            "fonte_sha256": context["fonte_ator"]["sha256_documento"],
            "opcoes": options,
            "justificativa": "Ataque validável apenas na fixture, pela ficha SRD pinada.",
        }
        rolls = {
            "evento_id": eid, "origem": "SIMULADO_EXTERNO_TESTE",
            "dados": dice,
        }
        return declaration, proposal, rolls

    def test_01_contexto_publico_nao_revela_cartas(self):
        context = contexto_publico(self.sessao)
        self.assertEqual(context["mesa"]["ator_da_vez"], "J2")
        self.assertEqual(context["contrato"], "ARBITRO_IA_BACKGROUND_V1")
        view = json.dumps(context, ensure_ascii=False)
        self.assertNotIn("CE-002", view)
        self.assertNotIn("AB-POC-001", view)
        self.assertNotIn("monte_ordem_ids", view)
        self.assertNotIn("minha_mao", view)

    def test_02_sem_modelo_injetado_job_aguarda_trabalho(self):
        status = self.job.processar_passo(None, None, None)
        self.assertEqual(status["estado"], "NA_FILA")
        self.assertEqual(status["passos_aceitos"], 0)
        self.assertFalse(self.sessao.motor.events[-1]["acao"].startswith("ATAQUE"))

    def test_03_ia_controladora_propoe_motor_executa(self):
        start = self.sessao.motor.state["versao"]
        d, p, r = self.get_package()
        out = self.job.processar_passo(d, p, r)
        self.assertEqual(out["decisao_ultimo_passo"], "ACEITA", out)
        self.assertEqual(out["estado"], "AGUARDANDO_JOGADOR")
        self.assertEqual(out["passos_aceitos"], 1)
        self.assertNotEqual(self.sessao.motor.state["versao"], start)
        self.assertEqual(self.sessao.motor.state["ator_da_vez"], "J1")
        self.assertEqual(out["historico_publico"][0]["ator"], "J2")

    def test_04_humano_nao_tem_turno_automatizado(self):
        d, p, r = self.get_package()
        self.job.processar_passo(d, p, r)
        original = copy.deepcopy(self.sessao.motor.state)
        status = self.job.processar_passo(None, None, None)
        self.assertEqual(status["estado"], "AGUARDANDO_JOGADOR")
        self.assertEqual(original, self.sessao.motor.state)

    def test_05_rollback_proposta_alterou_acao_do_jogador(self):
        d, p, r = self.get_package()
        p["comando"] = "TENTACLE_ROPER_TESTE"
        before = copy.deepcopy(self.sessao.motor.state)
        out = self.job.processar_passo(d, p, r)
        self.assertEqual(out["estado"], "FALHOU")
        self.assertEqual(before, self.sessao.motor.state)

    def test_06_rollback_fonte_falsificada(self):
        d, p, r = self.get_package()
        p["fonte_sha256"] = "0" * 64
        before = copy.deepcopy(self.sessao.motor.state)
        out = self.job.processar_passo(d, p, r)
        self.assertEqual(out["estado"], "FALHOU")
        self.assertEqual(before, self.sessao.motor.state)

    def test_07_rollback_versao_obsoleta(self):
        d, p, r = self.get_package()
        p["versao_estado"] = "E000"
        state = copy.deepcopy(self.sessao.motor.state)
        out = self.job.processar_passo(d, p, r)
        self.assertEqual(out["estado"], "FALHOU")
        self.assertEqual(state, self.sessao.motor.state)

    def test_08_rollback_hash_alterado(self):
        d, p, r = self.get_package()
        p["hash_estado"] = "HISTORICO_FALSO"
        state = copy.deepcopy(self.sessao.motor.state)
        self.assertEqual(
            self.job.processar_passo(d, p, r)["estado"], "FALHOU")
        self.assertEqual(state, self.sessao.motor.state)

    def test_09_proposta_nao_pode_injetar_resultado_ou_efeito(self):
        d, p, r = self.get_package()
        p["resultado"] = {"vencedor": "J2", "dano": 999}
        state = copy.deepcopy(self.sessao.motor.state)
        out = self.job.processar_passo(d, p, r)
        self.assertEqual(out["estado"], "FALHOU")
        self.assertEqual(state, self.sessao.motor.state)

    def test_10_ia_nao_pode_fornecer_dados_autoritativos(self):
        d, p, r = self.get_package()
        d["opcoes"]["d20_simulado"] = 20
        p["opcoes"]["d20_simulado"] = 20
        state = copy.deepcopy(self.sessao.motor.state)
        out = self.job.processar_passo(d, p, r)
        self.assertEqual(out["estado"], "FALHOU")
        self.assertEqual(state, self.sessao.motor.state)

    def test_11_origem_do_pacote_de_dados_incorreta(self):
        d, p, r = self.get_package()
        r["origem"] = "MODELO_IA"
        before = copy.deepcopy(self.sessao.motor.state)
        self.assertEqual(
            self.job.processar_passo(d, p, r)["estado"], "FALHOU")
        self.assertEqual(before, self.sessao.motor.state)

    def test_12_sem_dados_fica_aguardando_nao_muta(self):
        d, p, _ = self.get_package()
        before = copy.deepcopy(self.sessao.motor.state)
        out = self.job.processar_passo(d, p, None)
        self.assertEqual(out["estado"], "AGUARDANDO_DADOS")
        self.assertEqual(before, self.sessao.motor.state)
        self.assertEqual(out["passos_aceitos"], 0)

    def test_13_idempotencia_replay_mantem_um_unico_evento(self):
        d, p, r = self.get_package(eid="mesmo-evento-background")
        one = self.job.processar_passo(d, p, r)
        before_count = len(self.sessao.motor.events)
        two = self.job.processar_passo(d, p, r)
        self.assertEqual(one, two)
        self.assertEqual(len(self.sessao.motor.events), before_count)
        self.assertEqual(self.job.realizados, 1)

    def test_14_reuso_evento_com_rolagem_diferente_rejeitado(self):
        d, p, r = self.get_package(eid="conflito-background")
        self.job.processar_passo(d, p, r)
        state = copy.deepcopy(self.sessao.motor.state)
        other_roll = copy.deepcopy(r)
        other_roll["dados"]["d20_simulado"] = 20
        res = self.job.processar_passo(d, p, other_roll)
        self.assertEqual(res["estado"], "FALHOU")
        self.assertEqual(state, self.sessao.motor.state)

    def test_15_percurso_em_dois_turnos_e_ko(self):
        # 1. IA Roper erra; 2. humano Owl erra; 3. IA Roper crita/KO.
        self.job.processar_passo(*self.get_package(eid="turno-roper-1"))
        self.job.processar_passo(*self.get_package(
            options={"aceite_escopo": ESCOPO_BASICO, "ataque": "Talons"},
            eid="turno-owl-1",
        ))
        outcome = self.job.processar_passo(*self.get_package(
            dice={"d20_simulado": 20, "dano_dados": [8] * 6},
            eid="turno-roper-2",
        ))
        self.assertEqual(outcome["estado"], "CONCLUIDO")
        self.assertEqual(outcome["passos_aceitos"], 3)
        self.assertEqual(outcome["placar_fixture"], {"J1": 0, "J2": 1})
        self.assertEqual(
            self.sessao.motor.state["jogadores"]["J1"]["cartas"]["CE-001"]["zona"],
            "CEMITERIO",
        )
        self.assertTrue(self.sessao.motor.validate())

    def test_16_proposta_nao_pode_usurpar_comando_de_arbitro(self):
        d, p, r = self.get_package(
            command="INICIATIVA_ROPER_TESTE",
            options={"aceite_escopo": ESCOPO_BASICO},
            dice={},
        )
        old = copy.deepcopy(self.sessao.motor.state)
        self.assertEqual(
            self.job.processar_passo(d, p, r)["estado"], "FALHOU")
        self.assertEqual(old, self.sessao.motor.state)

    def test_17_execucao_lote_limite_e_espera_humano(self):
        first = self.get_package(eid="batch-first")
        out = self.job.processar_lote([first], limite_por_lote=1)
        self.assertEqual(out["passos_aceitos"], 1)
        self.assertEqual(out["estado"], "AGUARDANDO_JOGADOR")
        self.assertEqual(len(out["historico_publico"]), 1)

    def test_18_limite_passos_interrompe_sem_criar_eventos(self):
        self.job.max_passos = 1
        out = self.job.processar_passo(*self.get_package(eid="limit-one"))
        self.assertEqual(out["estado"], "PENDENTE_REGRA")
        self.assertEqual(out["passos_aceitos"], 1)
        original = copy.deepcopy(self.sessao.motor.state)
        self.job.processar_passo(None, None, None)
        self.assertEqual(original, self.sessao.motor.state)

    def test_19_pacote_nao_se_duplica_apos_restauro_motor(self):
        d, p, r = self.get_package(eid="restore-job")
        self.job.processar_passo(d, p, r)
        cp = self.sessao.checkpoint()
        restored = SessaoRoperFixture.restaurar(
            cp, self.source, self.contract,
        )
        self.assertEqual(restored.motor.state, self.sessao.motor.state)
        self.assertTrue(restored.motor.validate())

    def test_20_status_e_historico_sem_decks_ocultos(self):
        self.job.processar_passo(*self.get_package(eid="public-safe"))
        payload = json.dumps(self.job.status_publico(), ensure_ascii=False)
        self.assertNotIn("CE-002", payload)
        self.assertNotIn("AB-POC-001", payload)
        self.assertNotIn("monte_ordem_ids", payload)
        self.assertNotIn("minha_mao", payload)
        self.assertNotIn("justificativa", payload)

    def test_21_pendencia_concentracao_sem_dado_nao_muta(self):
        # Reconfigura fixture com J1 iniciando.
        self.sessao = SessaoRoperFixture.criar_de_checkout(
            self.source, self.contract, primeiro="J2",
            maos_fixadas={
                "J1": ["CE-001", "CE-002", "CE-003", "CE-004", "CE-005"],
                "J2": ["AB-POC-017", "AB-POC-001", "AB-POC-002",
                       "AB-POC-003", "AB-POC-004"],
            },
        )
        self.i = 100
        for p in ("J2", "J1"):
            self.ok(p, "TROCAR", {"descartar": []})
        for p, cid in (("J2", "AB-POC-017"), ("J1", "CE-001")):
            self.ok(p, "INVOCAR", {"carta_id": cid})
            self.ok(p, "PRONTO_CRIATURA")
        for p in ("J2", "J1"):
            self.ok(p, "ESCOLHER_SUPORTE", {"carta_id": None})
        for _ in range(2):
            self.ok("ARBITRO", "RESOLVER_SUPORTE_FIXTURE",
                    {"resultado": "PULAR"})
        self.ok("ARBITRO", "INICIATIVA_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "d20_simulados": {"J1": 20, "J2": 1},
        })
        job = JobSimulacao("concentration-rollback", self.sessao)
        self.assertEqual(self.sessao.motor.state["ator_da_vez"], "J1")
        p = self.get_package(
            "CONJURAR_MAGIA_OWL_TESTE",
            {"aceite_escopo": ESCOPO_CONJURACAO_OWL, "magia": "Detect Magic"},
            {}, "owl-cast-1",
        )
        self.assertEqual(job.processar_passo(*p)["passos_aceitos"], 1)
        self.assertEqual(self.sessao.motor.state["ator_da_vez"], "J2")
        old_state = copy.deepcopy(self.sessao.motor.state)
        old_head = self.sessao.motor.head_hash
        d, prop, dice = self.get_package(
            "ATAQUE_ROPER_BASICO_TESTE",
            {"aceite_escopo": ESCOPO_BASICO, "ataque": "Bite"},
            {"d20_simulado": 10, "dano_dados": [1, 1, 1]},
            "roper-requires-save",
        )
        out = job.processar_passo(d, prop, dice)
        self.assertEqual(out["estado"], "AGUARDANDO_DADOS", out)
        self.assertEqual(self.sessao.motor.state, old_state)
        self.assertEqual(self.sessao.motor.head_hash, old_head)

    def test_22_invariante_40_copias_em_cada_lado(self):
        self.job.processar_passo(*self.get_package(eid="forty-cards"))
        self.assertTrue(self.sessao.motor.validate())
        for side in ("J1", "J2"):
            self.assertEqual(
                len(self.sessao.motor.state["jogadores"][side]["cartas"]), 40
            )

    def test_23_nao_aceita_comando_pendente_como_executavel(self):
        self.assertNotIn("SPIDER_CLIMB_ROPER_TESTE", ACTIONS)
        self.assertNotIn("MULTIATTACK_ROPER_TESTE", ACTIONS)
        self.assertNotIn("Clairvoyance", ACTIONS)

    def test_24_nao_cria_jogo_oficial(self):
        self.assertTrue(self.sessao.motor.state["partida_id"].startswith("ASCEND"))
        self.assertEqual(self.sessao.motor.state["placar"], {"J1": 0, "J2": 0})
        self.assertEqual(self.job.status_publico()["partida"],
                         "FIXTURE_ISOLADA_NAO_OFICIAL")

    def test_25_retry_do_ko_concluido_nao_duplica_placar(self):
        self.job.processar_passo(*self.get_package(eid="antes-ko-ai"))
        self.job.processar_passo(*self.get_package(
            options={"aceite_escopo": ESCOPO_BASICO, "ataque": "Talons"},
            eid="antes-ko-humano",
        ))
        last = self.get_package(
            dice={"d20_simulado": 20, "dano_dados": [8] * 6},
            eid="ko-duplicado",
        )
        accepted = self.job.processar_passo(*last)
        self.assertEqual(accepted["estado"], "CONCLUIDO")
        events = len(self.sessao.motor.events)
        repeated = self.job.processar_passo(*last)
        self.assertEqual(repeated, accepted)
        self.assertEqual(len(self.sessao.motor.events), events)
        self.assertEqual(self.sessao.motor.state["placar"], {"J1": 0, "J2": 1})
        changed = copy.deepcopy(last)
        changed[2]["dados"]["d20_simulado"] = 19
        collision = self.job.processar_passo(*changed)
        self.assertEqual(collision["estado"], "CONCLUIDO")
        self.assertIn("colisão", collision["erro"])
        self.assertEqual(self.sessao.motor.state["placar"], {"J1": 0, "J2": 1})


if __name__ == "__main__":
    unittest.main()
