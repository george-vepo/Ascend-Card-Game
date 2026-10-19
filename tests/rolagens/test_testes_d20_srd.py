"""Resolução de dados explícitos para testes de atributo (sem fichas/RNG)."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from ascend.testes_d20_srd import (
    resolver_teste_atributo, TesteD20Invalido, TesteD20Pendente
)

def solve(conditions=None,rolls=None,mod=1,dc=14):
    return resolver_teste_atributo(
        condicoes=[] if conditions is None else conditions,
        dados=rolls,modificador=mod,cd=dc,
    )

class DadosDeAtributo(unittest.TestCase):
    def test_01_poisoned_impõe_desvantagem(self):
        r=solve(["Grappled","Poisoned"],[19,11])
        self.assertEqual((r["modo_rolagem"],r["d20_aplicado"]),
                         ("DESVANTAGEM",11))
        self.assertEqual(r["fonte_desvantagem"],"Poisoned")
        self.assertFalse(r["sucesso"])

    def test_02_o_menor_dado_define_sucesso(self):
        r=solve(["Poisoned"],[20,12],mod=1)
        self.assertEqual((r["total"],r["cd"]),(13,14))
        self.assertFalse(r["sucesso"])

    def test_03_ambos_dados_alcancam_cd(self):
        r=solve(["Poisoned"],[13,20],mod=1)
        self.assertTrue(r["sucesso"])
        self.assertEqual(r["total"],14)

    def test_04_acrobatics_contra_cd(self):
        r=solve(["Poisoned"],[20,12],mod=2)
        self.assertTrue(r["sucesso"])
        self.assertEqual(r["total"],14)

    def test_05_sem_poisoned_um_dado(self):
        r=solve(["Grappled"],[13])
        self.assertEqual((r["modo_rolagem"],r["d20_aplicado"]),("NORMAL",13))
        self.assertTrue(r["sucesso"])

    def test_06_sem_poisoned_dois_dados_nao_aceita(self):
        with self.assertRaises(TesteD20Pendente):
            solve(["Grappled"],[20,1])

    def test_07_poisoned_dado_ausente_pendente(self):
        with self.assertRaises(TesteD20Pendente):
            solve(["Poisoned"])

    def test_08_poisoned_dado_unico_pendente(self):
        with self.assertRaises(TesteD20Pendente):
            solve(["Poisoned"],[20])

    def test_09_d20_booleano_proibido(self):
        with self.assertRaises(TesteD20Invalido):
            solve(["Poisoned"],[True,20])

    def test_10_d20_zero_proibido(self):
        with self.assertRaises(TesteD20Invalido):
            solve(["Poisoned"],[0,20])

    def test_11_d20_21_proibido(self):
        with self.assertRaises(TesteD20Invalido):
            solve(["Poisoned"],[21,20])

    def test_12_condicoes_duplicadas_proibidas(self):
        with self.assertRaises(TesteD20Invalido):
            solve(["Poisoned","Poisoned"],[12,15])

    def test_13_modificador_nao_inventado(self):
        with self.assertRaises(TesteD20Invalido):
            solve(["Poisoned"],[12,18],mod=None)

    def test_14_cd_boleana_invalida(self):
        with self.assertRaises(TesteD20Invalido):
            solve(["Poisoned"],[12,18],dc=True)

    def test_15_saida_contém_dados_simulados(self):
        r=solve(["Poisoned"],[18,14])
        self.assertTrue(r["dados_simulados"])
        self.assertEqual(r["d20_simulados"],[18,14])

    def test_16_sem_rolagem_automatica(self):
        with self.assertRaises(TesteD20Pendente):
            solve(["Grappled"])

    def test_17_d20_natural_um_nao_é_erro_automático_do_teste(self):
        r=solve(["Poisoned"],[1,20],mod=14)
        self.assertTrue(r["sucesso"])
        self.assertEqual(r["total"],15)

if __name__=="__main__":
    unittest.main()
