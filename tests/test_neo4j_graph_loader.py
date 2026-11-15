import unittest

import pandas as pd

from graphdb.load_graph import build_payload, pseudonym


class GraphLoaderTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame(
            [
                {
                    "ds_os_status": "COBRADAS",
                    "veiculo_id": "vehicle-private-1",
                    "cd_estabelecimento": 101,
                    "cd_manutencao_oficina": 1,
                    "vl_aprovado_total": 125.5,
                    "ds_tipoestabelecimento": "OFICINA MECANICA",
                    "ds_familia": "PASSEIO",
                    "ds_veiculomodelo": "MODELO A",
                    "nr_anoveiculo": 2020,
                    "dt_transacao": "2024-01-03",
                },
                {
                    "ds_os_status": "COBRADAS",
                    "veiculo_id": "vehicle-private-1",
                    "cd_estabelecimento": 102,
                    "cd_manutencao_oficina": 2,
                    "vl_aprovado_total": 74.5,
                    "ds_tipoestabelecimento": "OFICINA MECANICA",
                    "ds_familia": "PASSEIO",
                    "ds_veiculomodelo": "MODELO A",
                    "nr_anoveiculo": 2020,
                    "dt_transacao": "2024-02-03",
                },
                {
                    "ds_os_status": "COBRADAS",
                    "veiculo_id": "vehicle-private-2",
                    "cd_estabelecimento": 101,
                    "cd_manutencao_oficina": 3,
                    "vl_aprovado_total": 25,
                    "ds_tipoestabelecimento": "OFICINA MECANICA",
                    "ds_familia": "CARGA",
                    "ds_veiculomodelo": "MODELO B",
                    "nr_anoveiculo": 2018,
                    "dt_transacao": "2024-03-03",
                },
                {
                    "ds_os_status": "CANCELADAS",
                    "veiculo_id": "vehicle-private-3",
                    "cd_estabelecimento": 103,
                    "cd_manutencao_oficina": 4,
                    "vl_aprovado_total": 500,
                    "ds_tipoestabelecimento": "OFICINA MECANICA",
                    "ds_familia": "PASSEIO",
                    "ds_veiculomodelo": "MODELO C",
                    "nr_anoveiculo": 2019,
                    "dt_transacao": "2024-04-03",
                },
            ]
        )
        self.frame["relato_gestor_auto"] = "note must not be persisted"
        self.frame["nome_motorista"] = "person must not be persisted"

    def test_builds_pseudonymous_bipartite_edges_and_shared_workshop_projection(self):
        payload = build_payload(self.frame, "test-secret")

        self.assertEqual(payload["source_rows"], 4)
        self.assertEqual(payload["charged_rows"], 3)
        self.assertEqual(payload["vehicle_count"], 2)
        self.assertEqual(payload["workshop_count"], 2)
        self.assertEqual(payload["service_edge_count"], 3)
        self.assertEqual(payload["projected_workshop_count"], 0)
        self.assertEqual(payload["shared_workshop_edge_count"], 0)
        self.assertEqual(payload["approved_value_sum"], 225.0)
        self.assertEqual(
            payload["service_edges"][0]["approved_value"],
            125.5,
        )
        serialized = repr(payload)
        self.assertNotIn("vehicle-private", serialized)
        self.assertNotIn("note must not be persisted", serialized)
        self.assertNotIn("person must not be persisted", serialized)

    def test_projection_requires_two_shared_vehicles(self):
        second_vehicle = self.frame.iloc[0].copy()
        second_vehicle["veiculo_id"] = "vehicle-private-2"
        second_vehicle["cd_estabelecimento"] = 102
        self.frame = pd.concat([self.frame, second_vehicle.to_frame().T], ignore_index=True)

        payload = build_payload(self.frame, "test-secret")

        self.assertEqual(payload["shared_workshop_edge_count"], 1)
        self.assertEqual(payload["shared_edges"][0]["shared_vehicle_count"], 2)

    def test_pseudonyms_are_stable_salted_and_namespaced(self):
        first = pseudonym("vehicle", "source-id", "secret-a")
        self.assertEqual(first, pseudonym("vehicle", "source-id", "secret-a"))
        self.assertNotEqual(first, pseudonym("vehicle", "source-id", "secret-b"))
        self.assertNotEqual(first, pseudonym("workshop", "source-id", "secret-a"))
        self.assertNotIn("source-id", first)


if __name__ == "__main__":
    unittest.main()
