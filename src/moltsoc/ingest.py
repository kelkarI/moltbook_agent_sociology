"""Phase 0 ingestion: download datasets, pin revisions, audit schemas.

Privacy: `owner_x_handle` is never read into reports; the audit skips it.
"""
import datetime as dt
import json
import pathlib
import sys

import duckdb
from huggingface_hub import HfApi, snapshot_download

RAW = pathlib.Path("data/raw")
MANIFEST = pathlib.Path("data/MANIFEST.json")
SOURCES = {
    "primary": "jscmp4/Moltbook",
    "graph": "takschdube/moltbook-dataset",
    "crosscheck": "SimulaMet/moltbook-observatory-archive",
}
DROP_COLS = {"owner_x_handle"}


def download() -> None:
    api, manifest = HfApi(), {}
    for role, repo in SOURCES.items():
        sha = api.dataset_info(repo).sha
        path = snapshot_download(repo, repo_type="dataset", revision=sha, local_dir=RAW / role,
                                 allow_patterns=["*.parquet", "*.csv", "*.json", "README.md"])
        manifest[role] = {"repo": repo, "revision": sha, "downloaded": dt.date.today().isoformat(), "local": str(path)}
    MANIFEST.write_text(json.dumps(manifest, indent=2))


def audit(role: str) -> dict:
    """Row count, schema, null rates, duplicate ids per parquet table (lazy, DuckDB)."""
    con, out = duckdb.connect(), {}
    for tdir in sorted(p for p in (RAW / role).rglob("*") if p.is_dir() and any(p.glob("*.parquet"))):
        glob = f"{tdir}/*.parquet"
        cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{glob}')").fetchall()
                if r[0] not in DROP_COLS]
        n = con.execute(f"SELECT count(*) FROM read_parquet('{glob}')").fetchone()[0]
        nulls = con.execute("SELECT " + ",".join(f'avg(("{c}" IS NULL)::int) AS "{c}"' for c in cols)
                            + f" FROM read_parquet('{glob}')").fetchdf().iloc[0].to_dict()
        dups = (con.execute(f"SELECT count(*)-count(DISTINCT id) FROM read_parquet('{glob}')").fetchone()[0]
                if "id" in cols else None)
        out[tdir.name] = {"rows": n, "columns": cols, "null_rate": nulls, "dup_ids": dups}
    return out


if __name__ == "__main__":
    if "--audit-only" not in sys.argv:
        download()
    pathlib.Path("reports/00_data_audit.json").write_text(
        json.dumps({r: audit(r) for r in SOURCES}, indent=2, default=str))
