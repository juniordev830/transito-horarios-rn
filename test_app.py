import json
from pathlib import Path
import subprocess
import sys
import unittest

from app import run

ROOT = Path(__file__).resolve().parent


class ProjetoTest(unittest.TestCase):
    def test_exemplo_documentado(self):
        data = json.loads((ROOT / "exemplo.json").read_text(encoding="utf-8"))
        result = run(data)
        self.assertEqual(result['melhor_faixa'], '09:00')

    def test_cli_com_exemplo(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "app.py"), str(ROOT / "exemplo.json")],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        self.assertEqual(json.loads(result.stdout)['melhor_faixa'], '09:00')

    def test_rejeita_dados_incompletos(self):
        with self.assertRaises((KeyError, ValueError, TypeError)):
            run({})

    def test_mediana_resiste_a_outlier(self):
        result = run(dict(origem="A", destino="B", faixas=[dict(hora="08:00", tempos=[10, 10, 100]), dict(hora="09:00", tempos=[20, 20])]))
        self.assertEqual(result["melhor_faixa"], "08:00")
        self.assertEqual(result["faixas"][0]["mediana_minutos"], 10)

    def test_rejeita_tempos_invalidos(self):
        for tempos in ([], [True], [-1], [float("nan")]):
            with self.subTest(tempos=tempos), self.assertRaises(ValueError):
                run(dict(origem="A", destino="B", faixas=[dict(hora="08:00", tempos=tempos)]))

    def test_exige_hora_local_estrita(self):
        for hora in ("8:00", "0800", "08:00:00", "24:00", "12:60", "08:00+00:00"):
            with self.subTest(hora=hora), self.assertRaisesRegex(ValueError, "HH:MM"):
                run(dict(origem="A", destino="B", faixas=[dict(hora=hora, tempos=[20])]))

    def test_rejeita_faixas_duplicadas_ou_vazias(self):
        with self.assertRaisesRegex(ValueError, "duplicada"):
            run(dict(origem="A", destino="B", faixas=[
                dict(hora="08:00", tempos=[20]), dict(hora="08:00", tempos=[22])]))
        with self.assertRaisesRegex(ValueError, "ao menos uma faixa"):
            run(dict(origem="A", destino="B", faixas=[]))
