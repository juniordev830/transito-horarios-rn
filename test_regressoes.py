import unittest
from app import run

class TimeWindowsTests(unittest.TestCase):
    def test_best_window_uses_median(self):
        result=run({"origem":"Natal","destino":"Parnamirim","faixas":[{"hora":"08:00","tempos":[40,50,60]},{"hora":"06:00","tempos":[20,25,30]}]})
        self.assertEqual(result["melhor_faixa"],"06:00")
        self.assertEqual(result["faixas"][0]["mediana_minutos"],25)

    def test_empty_observations_rejected(self):
        with self.assertRaises(ValueError):
            run({"origem":"Natal","destino":"Recife","faixas":[{"hora":"08:00","tempos":[]}]})

    def test_non_finite_observation_rejected(self):
        with self.assertRaises(ValueError):
            run({"origem":"Natal","destino":"Recife","faixas":[{"hora":"08:00","tempos":[float("nan")]}]})

if __name__ == "__main__": unittest.main()
