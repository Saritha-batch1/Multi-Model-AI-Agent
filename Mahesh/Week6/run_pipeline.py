"""
Mahesh / Week6 / run_pipeline.py
Week-6: Full Workflow Orchestrator

Runs:
Week1 → Week2 → Week3 → Week4 → Week5

Run from repo root:
    python Mahesh/Week6/run_pipeline.py
"""

import subprocess
from pathlib import Path
from datetime import datetime
import sys

# ==================================================
# PATH SETUP
# ==================================================

REPO_ROOT = Path(__file__).resolve().parents[2]

WEEK_SCRIPTS = [
    ("Week-1 Data Extraction", REPO_ROOT / "Mahesh/Week1/data_extraction_mahesh.py"),
    ("Week-2 OCR & Parsing", REPO_ROOT / "Mahesh/Week2/data_extraction_mahesh_v2.py"),
    ("Week-3 Pattern Recognition", REPO_ROOT / "Mahesh/Week3/pattern_recognition_mahesh.py"),
    ("Week-4 Contextual Analysis", REPO_ROOT / "Mahesh/Week4/contextual_analysis_mahesh(V4).py"),
    ("Week-5 Report Generation", REPO_ROOT / "Mahesh/Week5/report_generator_mahesh(V5).py"),
]

# ==================================================
# LOG FILE SETUP (TIMESTAMPED)
# ==================================================

LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

RUN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = LOGS_DIR / f"run_{RUN_TIMESTAMP}.log"

# ==================================================
# LOGGING UTILS (UNICODE-SAFE)
# ==================================================

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_message = message.encode("ascii", "ignore").decode()
    line = f"[{timestamp}] {safe_message}"

    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ==================================================
# PIPELINE RUNNER
# ==================================================

def run_script(step_name: str, script_path: Path):
    if not script_path.exists():
        log(f"[ERROR] {step_name} FAILED — script not found: {script_path}")
        raise FileNotFoundError(script_path)

    log(f"[START] {step_name}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.returncode != 0:
            log(f"[FAIL] {step_name}")
            if result.stderr:
                log("ERROR OUTPUT:")
                log(result.stderr.strip())
            raise RuntimeError(step_name)

        log(f"[SUCCESS] {step_name}")

        if result.stdout.strip():
            log("OUTPUT:")
            for line in result.stdout.splitlines():
                log(line)

    except Exception as e:
        log(f"[PIPELINE STOPPED] at {step_name}")
        raise e

# ==================================================
# MAIN PIPELINE
# ==================================================

def main():
    log("=" * 60)
    log("HEALTH REPORT PIPELINE STARTED")
    log(f"Log file: {LOG_FILE.name}")
    log("=" * 60)

    for step_name, script in WEEK_SCRIPTS:
        run_script(step_name, script)

    log("=" * 60)
    log("PIPELINE COMPLETED SUCCESSFULLY")
    log("=" * 60)

if __name__ == "__main__":
    main()
