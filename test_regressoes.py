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

    def test_reject_oversized_samples_before_sorting(self):
        payload = {"origem": "Natal", "destino": "Recife",
                   "faixas": [{"hora": "08:00", "tempos": [20] * 1001}]}
        with self.assertRaisesRegex(ValueError, "1000"):
            run(payload)

    def test_reject_excessive_time_windows(self):
        payload = {"origem": "Natal", "destino": "Recife",
                   "faixas": [{"hora": "08:00", "tempos": [30]}] * 1441}
        with self.assertRaisesRegex(ValueError, "1440"):
            run(payload)

    def test_boundary_of_1000_samples_is_supported(self):
        payload = {"origem": "Natal", "destino": "Recife",
                   "faixas": [{"hora": "07:30", "tempos": [15, 20] * 500}]}
        result = run(payload)
        self.assertEqual(result["faixas"][0]["observacoes"], 1000)
        self.assertEqual(result["faixas"][0]["mediana_minutos"], 17.5)


if __name__ == "__main__": unittest.main()
