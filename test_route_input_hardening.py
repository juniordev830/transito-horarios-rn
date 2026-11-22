import unittest
from urllib.parse import parse_qs, urlparse
from app import rota


class StrictRouteInputTests(unittest.TestCase):
    def test_rejects_non_string_route_modes(self):
        for value in (None, {}, [], True):
            with self.subTest(mode=value), self.assertRaises(ValueError):
                rota("Natal", "Parnamirim", modo=value)

    def test_requires_boolean_toll_option(self):
        for value in ("false", 0, 1, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                rota("Natal", "Parnamirim", evitar_pedagios=value)

    def test_requires_ordered_waypoints(self):
        for stops in ({"Natal", "Macau"}, {"stop": "Natal"}):
            with self.subTest(stops=stops), self.assertRaises(ValueError):
                rota("Natal", "Macau", paradas=stops)

    def test_keeps_valid_stop_order(self):
        query = parse_qs(urlparse(rota("Natal", "Touros", paradas=["Ceará-Mirim", "Maxaranguape"])).query)
        self.assertEqual(query["waypoints"], ["Ceará-Mirim|Maxaranguape"])


if __name__ == "__main__":
    unittest.main()
