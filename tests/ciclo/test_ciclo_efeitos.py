"""Contratos de ciclo de efeitos sem fichas, monstros ou dados gerados."""
import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))

from ascend.ciclo_efeitos import (
    CicloInvalido, CicloPendente, consumir_recurso, verificar_recarga,
    registrar_condicao, expirar_efeitos,
)

MAPA={"BLINDED_SPITTLE":"Blinded"}

def adicionar(conds=None,efeitos=None,fonte="AB-POC-008",turno=2):
    return registrar_condicao(
        [] if conds is None else conds, [] if efeitos is None else efeitos,
        marcador="BLINDED_SPITTLE",condicao="Blinded",
        fonte=fonte,expira_no_turno_fonte=turno,mapeamento=MAPA,
    )

def fim(conds,efeitos,fonte="AB-POC-008",turno=2):
    return expirar_efeitos(
        conds,efeitos,fonte=fonte,turno_fonte=turno,mapeamento=MAPA,
    )

class Recursos(unittest.TestCase):
    def test_01_consumo(self):
        self.assertIs(consumir_recurso(True),False)
    def test_02_sem_segundo_consumo(self):
        with self.assertRaises(CicloInvalido): consumir_recurso(False)
    def test_03_tipo_booleano_estrito(self):
        with self.assertRaises(CicloInvalido): consumir_recurso(1)
    def test_04_disponivel_dispensa_rolagem(self):
        self.assertEqual(verificar_recarga(True,None,faces=6,minimo=5,maximo=6),
                         (True,None))
    def test_05_dado_desnecessario_rejeita(self):
        with self.assertRaises(CicloInvalido):
            verificar_recarga(True,6,faces=6,minimo=5,maximo=6)
    def test_06_dado_pendente(self):
        with self.assertRaises(CicloPendente):
            verificar_recarga(False,None,faces=6,minimo=5,maximo=6)
    def test_07_recarga_quatro_nao_recarrega(self):
        novo,rel=verificar_recarga(False,4,faces=6,minimo=5,maximo=6)
        self.assertIs(novo,False)
        self.assertEqual(rel["dado"],4)
        self.assertFalse(rel["recarregou"])
    def test_08_recarga_cinco(self):
        novo,rel=verificar_recarga(False,5,faces=6,minimo=5,maximo=6)
        self.assertIs(novo,True)
        self.assertEqual(rel["minimo"],5)
        self.assertEqual(rel["faces"],6)
    def test_09_recarga_seis(self):
        self.assertTrue(verificar_recarga(False,6,faces=6,minimo=5,maximo=6)[0])
    def test_10_limites_vem_de_parametros(self):
        self.assertTrue(verificar_recarga(False,4,faces=6,minimo=4,maximo=6)[0])
    def test_11_booleano_nao_e_dado(self):
        with self.assertRaises(CicloInvalido):
            verificar_recarga(False,True,faces=6,minimo=5,maximo=6)
    def test_12_dado_fora_das_faces(self):
        with self.assertRaises(CicloInvalido):
            verificar_recarga(False,7,faces=6,minimo=5,maximo=6)
    def test_13_intervalo_invertido(self):
        with self.assertRaises(CicloInvalido):
            verificar_recarga(False,5,faces=6,minimo=6,maximo=5)
    def test_14_intervalo_supera_faces(self):
        with self.assertRaises(CicloInvalido):
            verificar_recarga(False,5,faces=6,minimo=5,maximo=7)

class Efeitos(unittest.TestCase):
    def test_15_adicionar_condicao_com_fonte(self):
        conds,ef=adicionar()
        self.assertEqual(conds,["Blinded"])
        self.assertEqual(ef[0]["fonte"],"AB-POC-008")
        self.assertEqual(ef[0]["condicao"],"Blinded")
        self.assertEqual(ef[0]["expira_ao_fim_turno_fonte"],2)
    def test_16_nao_muta_argumentos(self):
        c,e=[],[]
        nc,ne=adicionar(c,e)
        self.assertEqual((c,e),([],[]))
        self.assertIsNot(c,nc);self.assertIsNot(e,ne)
        old_c,old_e=copy.deepcopy(nc),copy.deepcopy(ne)
        fim(nc,ne)
        self.assertEqual(nc,old_c)
        self.assertEqual(ne,old_e)
    def test_17_nao_expira_no_turno_anterior(self):
        c,e=adicionar(turno=3)
        c2,e2,rem=fim(c,e,turno=2)
        self.assertEqual((c2,e2,rem),(c,e,[]))
    def test_18_expira_no_fim_turno_correto(self):
        c,e=adicionar(turno=2)
        self.assertEqual(fim(c,e),([],[],["Blinded"]))
    def test_19_virada_posterior_expira_tambem(self):
        c,e=adicionar(turno=2)
        self.assertEqual(fim(c,e,turno=3),([],[],["Blinded"]))
    def test_20_outra_fonte_nao_expira(self):
        c,e=adicionar()
        self.assertEqual(fim(c,e,fonte="OUTRA",turno=999),(c,e,[]))
    def test_21_reaplicar_renova_sem_duplicar(self):
        c,e=adicionar(turno=2)
        c,e=adicionar(c,e,turno=5)
        self.assertEqual(len(c),1)
        self.assertEqual(len(e),1)
        self.assertEqual(e[0]["expira_ao_fim_turno_fonte"],5)
        self.assertEqual(fim(c,e,turno=2),(c,e,[]))
    def test_22_duas_fontes_nao_apaga_condicao_antes(self):
        c,e=adicionar()
        c,e=adicionar(c,e,fonte="OUTRA",turno=5)
        c,e,rem=fim(c,e,turno=2)
        self.assertEqual(c,["Blinded"])
        self.assertEqual(len(e),1)
        self.assertEqual(rem,[])
        self.assertEqual(fim(c,e,fonte="OUTRA",turno=5),([],[],["Blinded"]))
    def test_23_efeito_legado_sem_campo_condicao(self):
        c,e=["Blinded"],[{
            "tipo":"BLINDED_SPITTLE","fonte":"AB-POC-008",
            "expira_ao_fim_turno_fonte":2,
        }]
        self.assertEqual(fim(c,e),([],[],["Blinded"]))
    def test_24_nao_aceita_mapeamento_ausente(self):
        with self.assertRaises(CicloInvalido):
            registrar_condicao([],[],marcador="UNKNOWN",condicao="Blinded",
                               fonte="J2",expira_no_turno_fonte=1,mapeamento=MAPA)
    def test_25_efeito_desconhecido_sem_mapeamento_pendente(self):
        c,e=adicionar()
        e.append({"tipo":"ANOTHER","fonte":"J2",
                  "expira_ao_fim_turno_fonte":2})
        with self.assertRaises(CicloPendente): fim(c,e)
    def test_26_condicao_explicita_contraditoria(self):
        c,e=adicionar()
        e[0]["condicao"]="Stunned"
        with self.assertRaises(CicloInvalido): fim(c,e)
    def test_27_expiracao_sem_condicao_ativa_rejeitada(self):
        c,e=adicionar()
        with self.assertRaises(CicloInvalido): fim([],e)
    def test_28_turno_zero_nao_expira(self):
        c,e=adicionar()
        self.assertEqual(fim(c,e,turno=0),(c,e,[]))
    def test_29_proibe_condicao_duplicada_no_estado(self):
        with self.assertRaises(CicloInvalido):
            adicionar(["Blinded","Blinded"],[])
    def test_30_proibe_efeito_duplicado_mesma_fonte(self):
        c,e=adicionar()
        e.append(copy.deepcopy(e[0]))
        with self.assertRaises(CicloInvalido): adicionar(c,e)

if __name__=="__main__":
    unittest.main()
