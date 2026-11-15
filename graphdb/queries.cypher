// Tamanho da rede bipartida efetivamente armazenada.
MATCH (v:FleetVehicle)-[r:SERVICED_AT]->(w:FleetWorkshop)
RETURN count(DISTINCT v) AS vehicles,
       count(DISTINCT w) AS workshops,
       count(r) AS vehicle_workshop_edges,
       sum(r.service_records) AS maintenance_records,
       round(sum(r.approved_value), 2) AS approved_value;

// Oficinas mais conectadas por veículos distintos.
MATCH (v:FleetVehicle)-[:SERVICED_AT]->(w:FleetWorkshop)
WITH w, count(DISTINCT v) AS connected_vehicles
RETURN w.key AS pseudonymous_workshop,
       w.kind AS establishment_type,
       connected_vehicles
ORDER BY connected_vehicles DESC
LIMIT 20;

// Pares de oficinas com veículos atendidos em comum.
MATCH (a:FleetWorkshop)-[r:SHARES_VEHICLE]->(b:FleetWorkshop)
RETURN a.key AS workshop_a,
       b.key AS workshop_b,
       r.shared_vehicle_count AS shared_vehicles
ORDER BY shared_vehicles DESC
LIMIT 20;

// Percorrer um veículo pseudonimizado e suas oficinas, sem expor o identificador original.
MATCH (v:FleetVehicle {key: $vehicle_key})-[r:SERVICED_AT]->(w:FleetWorkshop)
RETURN v.family AS vehicle_family,
       v.model AS vehicle_model,
       w.kind AS establishment_type,
       r.service_records AS maintenance_records,
       r.approved_value AS approved_value
ORDER BY r.approved_value DESC;
