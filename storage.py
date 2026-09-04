import csv
import json
from pathlib import Path
from typing import Iterable
from pydantic import BaseModel
from .config import EXPORT_DIR

def write_json(records: Iterable[BaseModel], path: Path):
    data = [r.model_dump(mode="json") for r in records]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def write_csv(records: Iterable[BaseModel], path: Path):
    data = [r.model_dump(mode="json") for r in records]
    path.parent.mkdir(parents=True, exist_ok=True)
    if not data:
        path.write_text("", encoding="utf-8")
        return
    # Flatten nested source/content dictionaries for spreadsheet friendliness.
    rows = []
    for item in data:
        row = {}
        for k, v in item.items():
            if isinstance(v, dict):
                for sk, sv in v.items():
                    row[f"{k}.{sk}"] = sv
            else:
                row[k] = v
        rows.append(row)

    fields = sorted({k for row in rows for k in row})
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
