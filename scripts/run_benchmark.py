"""Write repeatable MountainPilot benchmark results as JSON and CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from mountainpilot.evaluation import run_benchmark


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("results/latest"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = [record.as_dict() for record in run_benchmark()]

    json_path = args.output_dir / "benchmark.json"
    csv_path = args.output_dir / "benchmark.csv"
    json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} scenarios to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
