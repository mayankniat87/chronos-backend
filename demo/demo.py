"""
demo.py — run the full Member B pipeline against every sample decision and
print JSON output, exactly as Member C's /decisions/simulate route would
receive it (before the LLM explanation layer narrates it).

Usage:
    python demo.py                 # run all samples
    python demo.py accept_bulk_order   # run one named sample
"""

from __future__ import annotations

import sys

from app.engine import SimulationEngine
from app.engine.sample_data import ALL_SAMPLES


def run(name: str) -> None:
    builder = ALL_SAMPLES[name]
    decision = builder()
    engine = SimulationEngine()
    result = engine.run(decision)

    print(f"\n{'=' * 80}\nSCENARIO SET: {name}\n{'=' * 80}")
    print(result.model_dump_json(indent=2))


def main() -> None:
    if len(sys.argv) > 1:
        name = sys.argv[1]
        if name not in ALL_SAMPLES:
            print(f"Unknown sample '{name}'. Available: {list(ALL_SAMPLES)}")
            sys.exit(1)
        run(name)
    else:
        for name in ALL_SAMPLES:
            run(name)


if __name__ == "__main__":
    main()
