"""Parser estrito de texto SRD: APENAS fixtures sintéticas, sem fichas reais copiadas."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from ascend.fichas_srd import FichaConsultada, FichaConflitante
from ascend.perfil_combate_srd import extrair_perfil_de_combate

OWL = ("Large Celestial, Neutral\nAC 12\nInitiative +2 (12)\nHP 19 (3d10 + 3)\n"
       "Resistances Necrotic, Radiant\nActions\n"
       "Talons. Melee Attack Roll: +4, reach 5 ft. "
       "Hit: 7 (1d10 + 2) Slashing damage.\n")
MOUTH = ("Medium Aberration, Chaotic Neutral\nAC 9\nInitiative −1 (9)\n"
         "HP 52 (7d8 + 21)\nImmunities Prone\nActions\n"
         "Bite. Melee Attack Roll: +2, reach 5 ft. "
         "Hit: 7 (2d6)\nPiercing damage.\n")

def fonte(cid,txt,ac,pv,name):
    return FichaConsultada(
        id_copia=cid,id_catalogo="AT-TESTE",nome=name,
        tipo="Celestial" if cid=="CE-001" else "Aberração",
        nd="0.25" if cid=="CE-001" else "2",ca=ac,pv_maximos=pv,
        ficha_integral=txt,fonte="SRD-FIXTURE",versao="SRD 5.2.1",
        atribuicao="FIXTURE",editorial_review="AINDA_NAO_TESTADA_EM_ENGINE",
        sha256_documento="HASH-FICTICIO",revisao_git=None,
    )
def owl(txt=OWL):return fonte("CE-001",txt,12,19,"Giant Owl")
def mouth(txt=MOUTH):return fonte("AB-POC-008",txt,9,52,"Gibbering Mouther")

class ExtracaoEstrita(unittest.TestCase):
    def test_01_corujinha_dados(self):
        p=extrair_perfil_de_combate(owl())
        self.assertEqual(p["initiative"],2)
        self.assertEqual((p["ac"],p["hp"]),(12,19))
        self.assertEqual(p["attack"]["dice"],(1,10))
        self.assertEqual(p["attack"]["flat"],2)
        self.assertEqual(p["attack"]["bonus"],4)
        self.assertEqual(p["attack"]["type"],"Slashing")
        self.assertEqual(p["resistances"],["Necrotic","Radiant"])
        self.assertFalse(p["mechanics_fully_supported"])
    def test_02_mouther_unicode_menos(self):
        p=extrair_perfil_de_combate(mouth())
        self.assertEqual(p["initiative"],-1)
        self.assertEqual(p["attack"]["dice"],(2,6))
        self.assertEqual(p["attack"]["flat"],0)
        self.assertEqual(p["attack"]["type"],"Piercing")
        self.assertEqual(p["immunities"],[])
        self.assertEqual(p["condition_immunities"],["Prone"])
    def test_03_quebra_linha_dano(self):
        self.assertEqual(extrair_perfil_de_combate(mouth())["attack"]["bonus"],2)
    def test_04_iniciativa_ausente_pendente(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(owl(OWL.replace("Initiative +2 (12)","")))
    def test_05_dois_campos_iniciativa_pendente(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(owl(OWL.replace("Initiative +2 (12)","Initiative +2 (12)\nInitiative +2 (12)")))
    def test_06_ca_divergente(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(owl(OWL.replace("AC 12","AC 13")))
    def test_07_pv_divergente(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(owl(OWL.replace("HP 19","HP 20")))
    def test_08_ataque_ausente(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(owl(OWL.replace("Talons.","Peck.")))
    def test_09_dano_inventado_nao_aceito(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(owl(OWL.replace("1d10 + 2","8d10 + 2")))
    def test_10_tipo_dano_desconhecido(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(mouth(MOUTH.replace("Piercing","Acid")))
    def test_11_bonus_de_ataque_alterado_e_lido(self):
        p=extrair_perfil_de_combate(owl(OWL.replace("Roll: +4","Roll: +5")))
        self.assertEqual(p["attack"]["bonus"],5) # Não há valor fixo no parser!
    def test_12_resistencias_ausentes(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(owl(OWL.replace("Resistances Necrotic, Radiant","")))
    def test_13_imunidade_condicao_ausente(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(mouth(MOUTH.replace("Immunities Prone","")))
    def test_14_nd_outro_sem_template(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(fonte("AB-POC-031",MOUTH,9,52,"Outro"))
    def test_15_dois_ataques_com_mesmo_nome_pendente(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(owl(OWL+OWL.split("Actions\n")[1]))
    def test_16_tamanho_incompativel(self):
        with self.assertRaises(FichaConflitante):
            extrair_perfil_de_combate(owl(OWL.replace("Large Celestial","Medium Aberration")))
    def test_17_nome_da_acao_nao_e_dado_estatico(self):
        self.assertEqual(extrair_perfil_de_combate(owl())["attack"]["name"],"Talons")
    def test_18_alcance_lido(self):
        self.assertEqual(extrair_perfil_de_combate(mouth())["attack"]["reach_ft"],5)
    def test_19_tipo_de_dado_lido(self):
        self.assertEqual(extrair_perfil_de_combate(owl())["attack"]["dice"][1],10)
    def test_20_texto_incompleto_nao_considera_homologacao(self):
        self.assertFalse(extrair_perfil_de_combate(mouth())["mechanics_fully_supported"])

if __name__=="__main__": unittest.main()
