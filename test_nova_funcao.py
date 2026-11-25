import unittest
from app import run
class Variabilidade(unittest.TestCase):
    def test_faixas(self):
        data={"origem":"Natal","destino":"Macaíba","diagnostico":True,"faixas":[{"hora":"08:00","tempos":[10,20,30]},{"hora":"09:00","tempos":[5]}]}
        result=run(data,minimo_observacoes=2)
        self.assertEqual(result["melhor_faixa"],"08:00")
        self.assertEqual(result["faixas"][1]["amplitude_minutos"],20)
        self.assertFalse(result["faixas"][0]["amostra_suficiente"])
