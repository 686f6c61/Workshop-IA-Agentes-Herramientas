#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_manifest():
    text = (ROOT / "ops/ai/manifest.yaml").read_text(encoding="utf-8")
    # Parser mínimo para este ejercicio: valida presencia de claves, no YAML completo.
    return {
        "service": "service:" in text,
        "release": "release:" in text,
        "owner": "owner:" in text,
        "slo": "latency_p95_ms:" in text and "contract_fail_rate_max:" in text,
        "rollback": "last_known_good:" in text and "tested: true" in text,
        "evalops": "release_gate:" in text,
        "observability": "required_trace_attributes:" in text,
    }


def main():
    checks = read_manifest()
    decision = "ready_for_smoke" if all(checks.values()) else "missing_operational_contract"
    report = {"checks": checks, "decision": decision}
    out = ROOT / "output/c01_release_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
