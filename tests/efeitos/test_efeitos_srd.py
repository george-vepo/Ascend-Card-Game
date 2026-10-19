"""Parâmetros SRD extraídos em fixtures SINTÉTICAS; sem fichas copiadas."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from ascend.fichas_srd import FichaConsultada, FichaConflitante
from ascend.efeitos_srd import extrair_salvaguardas_celestial, extrair_efeitos_gibbering

OWL=("Giant Owl | TESTE\nLarge Celestial, Neutral\n"
     "Dex 15 +2 +2; Wis 14 +2 +4\nActions\nTalons. TESTE\n")
MOUTH=(
    "Gibbering Mouther | TESTE\nTraits\n"
    "Gibbering. The mouther babbles incoherently. "
    "Wisdom Saving Throw: DC 10, any creature that starts its turn within "
    "20 feet of the mouther while it is babbling. Failure: The target "
    "rolls 1d8 to determine what it does during the current turn: "
    "1–4. The target does nothing. 5–6. The target takes no action. "
    "7–8. The target makes a melee attack against a randomly determined "
    "creature within its reach or does nothing.\n"
    "Actions\n"
    "Bite. TESTE. "
    "Blinding Spittle (Recharge 5–6). Dexterity Saving Throw: DC 10, "
    "each creature in a 10-foot-radius Sphere centered on a point within "
    "30 feet. Failure: 7 (2d6) Radiant damage, and the target has the "
    "Blinded condition until the end of the mouther’s next turn.\n"
)

def ficha(cid, name, txt):
    return FichaConsultada(
        id_copia=cid,id_catalogo="FONTE-SINTETICA",nome=name,
        tipo="Celestial" if cid=="CE-001" else "Aberração",nd="2",
        ca=12,pv_maximos=19,ficha_integral=txt,fonte="FIXTURE",
        versao="SRD 5.2.1",atribuicao="FIXTURE-NÃO-OFICIAL",
        editorial_review="AINDA_NAO_TESTADA_EM_ENGINE",
        sha256_documento="HASH-SINTETICO",revisao_git=None,
    )
def owl(txt=OWL):return ficha("CE-001","Giant Owl",txt)
def mouth(txt=MOUTH):return ficha("AB-POC-008","Gibbering Mouther",txt)

class TestFonteDasSalvaguardas(unittest.TestCase):
    def test_01_bonus_owl_saem_de_texto(self):
        self.assertEqual(extrair_salvaguardas_celestial(owl()),
                         {"dex_bonus":2,"wis_bonus":4})
    def test_02_bonus_sab_alterado_na_fixture_e_lido(self):
        self.assertEqual(extrair_salvaguardas_celestial(
            owl(OWL.replace("Wis 14 +2 +4","Wis 14 +2 +5")))["wis_bonus"],5)
    def test_03_bonus_des_alterado_e_lido(self):
        self.assertEqual(extrair_salvaguardas_celestial(
            owl(OWL.replace("Dex 15 +2 +2","Dex 15 +2 +3")))["dex_bonus"],3)
    def test_04_bonus_sab_ausente_nao_inferido(self):
        with self.assertRaises(FichaConflitante):
            extrair_salvaguardas_celestial(owl(OWL.replace("Wis 14 +2 +4","")))
    def test_05_bonus_des_duplicado_nao_aceito(self):
        with self.assertRaises(FichaConflitante):
            extrair_salvaguardas_celestial(owl(OWL+"Dex 15 +2 +2"))
    def test_06_rejeita_ficha_homonima(self):
        with self.assertRaises(FichaConflitante):
            extrair_salvaguardas_celestial(ficha("CE-002","Outra",OWL))

class TestFonteDosEfeitos(unittest.TestCase):
    def test_07_parses_gibbering(self):
        p=extrair_efeitos_gibbering(mouth())["gibbering"]
        self.assertEqual(p,{"dc":10,"range_ft":20,"d8_faces":8})
    def test_08_parses_spittle(self):
        p=extrair_efeitos_gibbering(mouth())["spittle"]
        self.assertEqual(p["dc"],10)
        self.assertEqual((p["radius_ft"],p["range_ft"]),(10,30))
        self.assertEqual(p["damage_dice"],(2,6))
        self.assertEqual(p["damage_type"],"Radiant")
        self.assertEqual((p["recharge_min"],p["recharge_max"]),(5,6))
        self.assertTrue(p["blinded_termina_no_proximo_turno_fonte"])
    def test_09_cd_sab_lida_nao_esta_fixa(self):
        p=extrair_efeitos_gibbering(mouth(
            MOUTH.replace("Wisdom Saving Throw: DC 10","Wisdom Saving Throw: DC 12")))
        self.assertEqual(p["gibbering"]["dc"],12)
    def test_10_cd_des_lida_nao_esta_fixa(self):
        p=extrair_efeitos_gibbering(mouth(
            MOUTH.replace("Dexterity Saving Throw: DC 10","Dexterity Saving Throw: DC 13")))
        self.assertEqual(p["spittle"]["dc"],13)
    def test_11_recarga_lida_da_fonte(self):
        p=extrair_efeitos_gibbering(mouth(
            MOUTH.replace("Recharge 5–6","Recharge 4–6")))
        self.assertEqual((p["spittle"]["recharge_min"],p["spittle"]["recharge_max"]),(4,6))
    def test_12_ausencia_cd_gibbering_bloqueia(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(
                MOUTH.replace("Wisdom Saving Throw: DC 10","Wisdom Saving Throw: DC XX")))
    def test_13_ausencia_cd_spittle_bloqueia(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(
                MOUTH.replace("Dexterity Saving Throw: DC 10","Dexterity Saving Throw: ???")))
    def test_14_duplicata_spittle_bloqueia(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(MOUTH+MOUTH.split("Blinding Spittle")[1].join(["Blinding Spittle",""])))
    def test_15_raio_ausente_bloqueia(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(
                MOUTH.replace("10-foot-radius Sphere","unspecified Sphere")))
    def test_16_tipo_dano_nao_implementado_bloqueia(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(MOUTH.replace("Radiant damage","Cold damage")))
    def test_17_dado_dano_sem_media_consistente_bloqueia(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(MOUTH.replace("7 (2d6)","7 (3d6)")))
    def test_18_resultado_78_obrigatorio_na_fonte(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(
                MOUTH.replace("7–8. The target makes","7–8. Unspecified effect; target makes")))
    def test_19_duracao_sem_texto_exato_bloqueia(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(
                MOUTH.replace("end of the mouther’s next turn","end of the current turn")))
    def test_20_nao_aceitar_recarga_impossivel(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(MOUTH.replace("Recharge 5–6","Recharge 7–8")))
    def test_21_sem_nome_de_efeito_bloqueia(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(MOUTH.replace("Gibbering.","Unspecified.")))
    def test_22_duplicado_gibbering_bloqueia(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(MOUTH.replace("Gibbering.","Gibbering. Gibbering.")))
    def test_23_ficha_outro_id_bloqueada(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(ficha("AB-POC-017","Roper",MOUTH))
    def test_24_salvaguarda_d8_nao_muda_para_outra_face(self):
        with self.assertRaises(FichaConflitante):
            extrair_efeitos_gibbering(mouth(MOUTH.replace("rolls 1d8","rolls 1d6")))

if __name__=="__main__":
    unittest.main()
