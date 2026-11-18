import json
from pathlib import Path
import subprocess
import sys
import unittest

from app import run


class HistoricoMinimoTest(unittest.TestCase):
    def setUp(self):
        self.dados = {"origem": "A", "destino": "B", "faixas": [
            {"hora": "06:00", "tempos": [8]},
            {"hora": "07:00", "tempos": [20, 30]},
            {"hora": "08:00", "tempos": [30, 25, 20]},
        ]}

    def test_so_recomenda_horarios_com_historico_suficiente(self):
        original = run(self.dados)
        self.assertEqual(original["melhor_faixa"], "06:00")
        for minimo in (2, 3):
            resultado = run(self.dados, minimo_observacoes=minimo)
            self.assertEqual(resultado["melhor_faixa"], "08:00")
            self.assertEqual(resultado["faixas"], original["faixas"])

    def test_amostra_insuficiente_preserva_observacoes(self):
        resultado = run(self.dados, minimo_observacoes=4)
        self.assertIsNone(resultado["melhor_faixa"])
        self.assertEqual(len(resultado["faixas"]), 3)

    def test_minimo_invalido(self):
        for minimo in (0, -1, True, 1.5):
            with self.subTest(minimo=minimo), self.assertRaises(ValueError):
                run(self.dados, minimo_observacoes=minimo)

    def test_cli(self):
        root = Path(__file__).resolve().parent
        comando = [sys.executable, root / "app.py", root / "exemplo.json", "--minimo-observacoes"]
        resultado = subprocess.run([*comando, "4"], capture_output=True, check=True)
        self.assertIsNone(json.loads(resultado.stdout)["melhor_faixa"])
        invalido = subprocess.run([*comando, "0"], capture_output=True)
        self.assertEqual(invalido.returncode, 2)
        self.assertFalse(invalido.stdout)
