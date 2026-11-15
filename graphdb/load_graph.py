#!/usr/bin/env python3
"""Load a privacy-minimized vehicle/workshop graph into a local Neo4j instance."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import sys
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "dissertacao_frotas/dados/processados/os_consolidadas_processadas.parquet"
DEFAULT_REPORT = ROOT / "dissertacao_frotas/resultados/logs/relatorio_neo4j_grafo.json"
ENV_FILE = Path(__file__).resolve().parent / ".env"
BATCH_SIZE = 1000
NEO4J_DATABASE = "neo4j"

SOURCE_COLUMNS = [
    "ds_os_status",
    "veiculo_id",
    "cd_estabelecimento",
    "cd_manutencao_oficina",
    "vl_aprovado_total",
    "ds_tipoestabelecimento",
    "ds_familia",
    "ds_veiculomodelo",
    "nr_anoveiculo",
    "dt_transacao",
]


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def initialize_env_file(path: Path = ENV_FILE) -> None:
    if path.exists():
        raise FileExistsError(f"{path} already exists; refusing to overwrite local secrets.")
    path.write_text(
        f"NEO4J_PASSWORD={secrets.token_hex(32)}\n"
        f"GRAPH_ID_SALT={secrets.token_hex(32)}\n",
        encoding="utf-8",
    )
    path.chmod(0o600)


def _source_id(value: Any) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip() or None


def _text(value: Any) -> str | None:
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value or None


def _year(value: Any) -> int | None:
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError, OverflowError):
        return None


def pseudonym(prefix: str, raw_id: str, salt: str) -> str:
    digest = hmac.new(salt.encode("utf-8"), raw_id.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{prefix}-{digest[:32]}"


def _iso_date(value: Any) -> str | None:
    if pd.isna(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.isoformat()


def build_payload(frame: pd.DataFrame, salt: str) -> dict[str, Any]:
    required = set(SOURCE_COLUMNS)
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Source is missing required columns: {', '.join(missing)}")

    active = frame.loc[frame["ds_os_status"].astype("string").str.upper().eq("COBRADAS")].copy()
    active["vehicle_source_id"] = active["veiculo_id"].map(_source_id)
    active["workshop_source_id"] = active["cd_estabelecimento"].map(_source_id)
    active = active.dropna(subset=["vehicle_source_id", "workshop_source_id"])
    if active.empty:
        raise ValueError("No charged maintenance records with both vehicle and workshop identifiers.")

    active["approved_value"] = pd.to_numeric(active["vl_aprovado_total"], errors="coerce").fillna(0.0)
    active["event_date"] = pd.to_datetime(active["dt_transacao"], errors="coerce")

    vehicle_rows = (
        active.drop_duplicates("vehicle_source_id")
        .set_index("vehicle_source_id")
        .to_dict("index")
    )
    vehicles = [
        {
            "key": pseudonym("vehicle", source_id, salt),
            "family": _text(row.get("ds_familia")),
            "model": _text(row.get("ds_veiculomodelo")),
            "year": _year(row.get("nr_anoveiculo")),
        }
        for source_id, row in vehicle_rows.items()
    ]

    workshop_rows = (
        active.drop_duplicates("workshop_source_id")
        .set_index("workshop_source_id")
        .to_dict("index")
    )
    workshops = [
        {
            "key": pseudonym("workshop", source_id, salt),
            "kind": _text(row.get("ds_tipoestabelecimento")),
        }
        for source_id, row in workshop_rows.items()
    ]

    grouped = (
        active.groupby(["vehicle_source_id", "workshop_source_id"], sort=True)
        .agg(
            service_records=("cd_manutencao_oficina", "count"),
            approved_value=("approved_value", "sum"),
            first_seen=("event_date", "min"),
            last_seen=("event_date", "max"),
        )
        .reset_index()
    )
    service_edges = [
        {
            "vehicle_key": pseudonym("vehicle", row.vehicle_source_id, salt),
            "workshop_key": pseudonym("workshop", row.workshop_source_id, salt),
            "service_records": int(row.service_records),
            "approved_value": round(float(row.approved_value), 2),
            "first_seen": _iso_date(row.first_seen),
            "last_seen": _iso_date(row.last_seen),
        }
        for row in grouped.itertuples(index=False)
    ]

    workshop_ids_by_vehicle = grouped.groupby("vehicle_source_id")["workshop_source_id"]
    shared_vehicles: dict[tuple[str, str], int] = defaultdict(int)
    for source_ids in workshop_ids_by_vehicle:
        ids = sorted(set(source_ids[1]))
        for left, right in combinations(ids, 2):
            shared_vehicles[(left, right)] += 1

    shared_edges = [
        {
            "workshop_key_a": pseudonym("workshop", left, salt),
            "workshop_key_b": pseudonym("workshop", right, salt),
            "shared_vehicle_count": count,
            "weight": float(count),
        }
        for (left, right), count in sorted(shared_vehicles.items())
        if count >= 2
    ]

    projected_workshop_keys = {
        key
        for edge in shared_edges
        for key in (edge["workshop_key_a"], edge["workshop_key_b"])
    }
    return {
        "source_rows": int(len(frame)),
        "charged_rows": int(len(active)),
        "vehicle_count": len(vehicles),
        "workshop_count": len(workshops),
        "service_edge_count": len(service_edges),
        "projected_workshop_count": len(projected_workshop_keys),
        "shared_workshop_edge_count": len(shared_edges),
        "approved_value_sum": round(float(grouped["approved_value"].sum()), 2),
        "vehicles": vehicles,
        "workshops": workshops,
        "service_edges": service_edges,
        "shared_edges": shared_edges,
    }


def _chunks(rows: list[dict[str, Any]], size: int = BATCH_SIZE):
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def _write_rows(session, query: str, rows: list[dict[str, Any]]) -> None:
    for batch in _chunks(rows):
        session.execute_write(lambda tx: tx.run(query, rows=batch).consume())


def load_into_neo4j(payload: dict[str, Any], replace: bool = False) -> dict[str, int]:
    uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        raise ValueError("NEO4J_PASSWORD is required; initialize graphdb/.env first.")
    if not _is_loopback_uri(uri) and os.getenv("ALLOW_REMOTE_NEO4J") != "1":
        raise ValueError("This loader is local-only. Set ALLOW_REMOTE_NEO4J=1 only after an explicit security review.")

    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        driver.verify_connectivity()
        with driver.session(database=NEO4J_DATABASE) as session:
            session.run(
                "CREATE CONSTRAINT fleet_vehicle_key IF NOT EXISTS "
                "FOR (n:FleetVehicle) REQUIRE n.key IS UNIQUE"
            ).consume()
            session.run(
                "CREATE CONSTRAINT fleet_workshop_key IF NOT EXISTS "
                "FOR (n:FleetWorkshop) REQUIRE n.key IS UNIQUE"
            ).consume()
            if replace:
                session.run(
                    "MATCH (n) WHERE n:FleetVehicle OR n:FleetWorkshop "
                    "DETACH DELETE n"
                ).consume()

            _write_rows(
                session,
                "UNWIND $rows AS row "
                "MERGE (n:FleetVehicle {key: row.key}) "
                "SET n.family = row.family, n.model = row.model, n.year = row.year",
                payload["vehicles"],
            )
            _write_rows(
                session,
                "UNWIND $rows AS row "
                "MERGE (n:FleetWorkshop {key: row.key}) "
                "SET n.kind = row.kind",
                payload["workshops"],
            )
            _write_rows(
                session,
                "UNWIND $rows AS row "
                "MATCH (v:FleetVehicle {key: row.vehicle_key}) "
                "MATCH (w:FleetWorkshop {key: row.workshop_key}) "
                "MERGE (v)-[r:SERVICED_AT]->(w) "
                "SET r.service_records = row.service_records, "
                "r.approved_value = row.approved_value, "
                "r.first_seen = row.first_seen, r.last_seen = row.last_seen",
                payload["service_edges"],
            )
            _write_rows(
                session,
                "UNWIND $rows AS row "
                "MATCH (a:FleetWorkshop {key: row.workshop_key_a}) "
                "MATCH (b:FleetWorkshop {key: row.workshop_key_b}) "
                "MERGE (a)-[r:SHARES_VEHICLE]->(b) "
                "SET r.shared_vehicle_count = row.shared_vehicle_count, r.weight = row.weight",
                payload["shared_edges"],
            )

            result = session.run(
                "MATCH (v:FleetVehicle)-[s:SERVICED_AT]->(w:FleetWorkshop) "
                "WITH count(DISTINCT v) AS vehicles, count(DISTINCT w) AS workshops, "
                "count(s) AS service_edges "
                "CALL () { "
                "MATCH (a:FleetWorkshop)-[p:SHARES_VEHICLE]->(b:FleetWorkshop) "
                "RETURN count(p) AS projected_edges "
                "} "
                "CALL () { "
                "MATCH (node:FleetWorkshop)-[:SHARES_VEHICLE]-() "
                "RETURN count(DISTINCT node) AS projected_workshops "
                "} "
                "RETURN vehicles, workshops, service_edges, projected_workshops, projected_edges"
            ).single()
            if result is None:
                raise RuntimeError("Neo4j did not return graph verification counts.")
            actual = {
                "vehicle_count": result["vehicles"],
                "workshop_count": result["workshops"],
                "service_edge_count": result["service_edges"],
                "projected_workshop_count": result["projected_workshops"],
                "shared_workshop_edge_count": result["projected_edges"],
            }
    finally:
        driver.close()

    expected = {key: payload[key] for key in actual}
    if actual != expected:
        raise RuntimeError(f"Neo4j graph verification failed: expected {expected}, received {actual}")
    return actual


def _is_loopback_uri(uri: str) -> bool:
    from urllib.parse import urlparse

    return urlparse(uri).hostname in {"localhost", "127.0.0.1", "::1"}


def write_report(payload: dict[str, Any], source: Path, actual: dict[str, int], report: Path) -> None:
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": str(source.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "database": NEO4J_DATABASE,
        "graph_model": {
            "nodes": ["FleetVehicle", "FleetWorkshop"],
            "relationships": ["SERVICED_AT", "SHARES_VEHICLE"],
            "projection_threshold": "At least two shared vehicles per workshop pair",
            "identity_protection": "HMAC-SHA256 with local GRAPH_ID_SALT; raw source identifiers are not stored",
            "excluded_fields": [
                "license plates",
                "names",
                "tax identifiers",
                "free-text notes",
                "fuel transactions",
            ],
        },
        "source_counts": {
            "rows_read": payload["source_rows"],
            "charged_rows_with_both_ids": payload["charged_rows"],
            "approved_value_total_reais": payload["approved_value_sum"],
        },
        "verified_neo4j_counts": actual,
        "interpretation": (
            "Counts describe the imported, filtered graph and are not evidence of wrongdoing, "
            "causality, or real-world impact."
        ),
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--replace", action="store_true", help="Replace only FleetVehicle/FleetWorkshop graph nodes.")
    parser.add_argument("--init-env", action="store_true", help="Create local Neo4j credentials and pseudonymization salt.")
    args = parser.parse_args()

    if args.init_env:
        try:
            initialize_env_file()
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(f"Created local secrets at {ENV_FILE}; file permissions set to 0600.")
        return 0

    load_env_file()
    salt = os.getenv("GRAPH_ID_SALT")
    if not salt:
        print("GRAPH_ID_SALT is required; initialize graphdb/.env first.", file=sys.stderr)
        return 2
    if not args.source.is_file():
        print(f"Processed source file not found: {args.source}", file=sys.stderr)
        return 2

    frame = pd.read_parquet(args.source, columns=SOURCE_COLUMNS)
    payload = build_payload(frame, salt)
    actual = load_into_neo4j(payload, replace=args.replace)
    write_report(payload, args.source, actual, args.report)
    print(json.dumps({"imported": actual, "report": str(args.report)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
