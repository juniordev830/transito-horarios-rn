import unittest
from app import rota, run


class RouteTextBoundsTests(unittest.TestCase):
    def test_rejects_control_characters_in_addresses(self):
        for address in ("Natal\nRN", "Natal\x00RN", "Natal\x7fRN"):
            with self.subTest(address=repr(address)), self.assertRaises(ValueError):
                rota(address, "Parnamirim")

    def test_rejects_oversized_address(self):
        with self.assertRaisesRegex(ValueError, "300"):
            rota("A" * 301, "Parnamirim")

    def test_does_not_change_normal_windows(self):
        result = run({"origem": " Natal ", "destino": "Parnamirim",
                      "faixas": [{"hora": "09:00", "tempos": [20]}]})
        self.assertEqual(result["melhor_faixa"], "09:00")


if __name__ == "__main__":
    unittest.main()
