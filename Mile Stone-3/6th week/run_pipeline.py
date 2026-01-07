"""
 ##  Full Workflow Integration & Orchestration (Model-5)

- Runs Week-1 → Week-5 sequentially
- Unicode-safe logging
- Timestamped execution logs
- Stops safely on failure
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import traceback

# ==================================================
# BASE PATH
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[1]
LOGS_DIR = BASE_DIR / "Week6" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

RUN_TS = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = LOGS_DIR / f"run_{RUN_TS}.log"

# ==================================================
# PIPELINE DEFINITION
# ==================================================

PIPELINE_STEPS = [
    ("Week-1 Data Extraction", BASE_DIR / "1st week" / "data_extraction.py"),
    ("Week-2 OCR & Parsing", BASE_DIR / "2nd week" / "data_extraction_week2.py"),
    ("Week-3 Pattern Recognition", BASE_DIR / "3rd week" / "recognition_pattern.py"),
    ("Week-4 Contextual Analysis", BASE_DIR / "4th week" / "contextual_analysis.py"),
    ("Week-5 Report Generation", BASE_DIR / "5th week" / "Synthesis_recommendation.py"),
]


# ==================================================
# LOGGING (UNICODE SAFE)
# ==================================================

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"

    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ==================================================
# RUN SINGLE STEP
# ==================================================

def run_step(name: str, script: Path):
    log("=" * 60)
    log(f"STARTING {name}")

    if not script.exists():
        raise FileNotFoundError(f"{name} script not found → {script}")

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        if result.stdout:
            log("[STDOUT]")
            for line in result.stdout.splitlines():
                log(line)

        if result.stderr:
            log("[STDERR]")
            for line in result.stderr.splitlines():
                log(line)

        if result.returncode != 0:
            raise RuntimeError(f"{name} failed with exit code {result.returncode}")

        log(f"{name} COMPLETED SUCCESSFULLY")

    except Exception as e:
        log(f"❌ ERROR IN {name}: {e}")
        log(traceback.format_exc())
        raise  # stop pipeline safely

# ==================================================
# MAIN ORCHESTRATOR
# ==================================================

def main():
    log("=" * 60)
    log("HEALTH REPORT ANALYSIS PIPELINE STARTED")
    log(f"Log file: {LOG_FILE.name}")
    log("=" * 60)

    for step_name, script in PIPELINE_STEPS:
        run_step(step_name, script)

    log("=" * 60)
    log("PIPELINE COMPLETED SUCCESSFULLY")
    log("Final user reports available in Week-5/output")
    log("=" * 60)

# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()
