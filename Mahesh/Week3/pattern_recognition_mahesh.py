"""
pattern_recognition_mahesh.py
Week-3: Pattern recognition & basic risk scores (uses Week-2 outputs)

Run:
  cd "M:\mahesh\Intenships\Infosys Internship"
  . .\.venv\Scripts\Activate.ps1
  python "Mahesh\Week3\pattern_recognition_mahesh.py"
"""

from pathlib import Path
from datetime import datetime
import json
import statistics
import math

# ----------------- Helpers: config + folder discovery -----------------
def load_config(repo_root=None):
    root = Path(repo_root or Path('.').resolve())
    cfg_path = root / "config.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"config.json not found at {cfg_path.resolve()}")
    return json.loads(cfg_path.read_text(encoding='utf-8'))

def find_week2_json_folder(cfg):
    repo_root = Path(cfg.get('repo_root', '.')).resolve()
    candidates = cfg.get('week2_candidates', [])
    found = []
    for p in candidates:
        cand = (repo_root / p).resolve()
        if cand.exists() and any(cand.glob('*.json')):
            found.append(cand)
    if not found:
        # fallback: search repo for row_reports with JSONs
        for p in repo_root.rglob('row_reports'):
            if any(p.glob('*.json')):
                found.append(p)
    if not found:
        raise FileNotFoundError(
            "Could not find week2 JSON outputs. Checked:\n- " +
            "\n- ".join([str((repo_root / p).resolve()) for p in candidates])
        )
    # return the candidate with most JSON files (best guess)
    found_sorted = sorted(found, key=lambda d: sum(1 for _ in d.glob('*.json')), reverse=True)
    return found_sorted[0]

# ----------------- Simple pattern & risk utilities -----------------
def safe_float(x):
    try:
        return float(str(x).strip())
    except Exception:
        return None

def cholesterol_ratio(total_chol, hdl=None, ldl=None):
    # prefer total/hdl if available
    t = safe_float(total_chol)
    h = safe_float(hdl)
    l = safe_float(ldl)
    if t is None:
        return None
    if h:
        return round(t / h, 2) if h != 0 else None
    if l:
        # crude approximate if HDL not present: no stable formula, return None
        return None
    return None

def glucose_category(glucose_mgdl):
    g = safe_float(glucose_mgdl)
    if g is None:
        return None
    if g < 100:
        return "normal"
    if 100 <= g <= 125:
        return "prediabetes"
    return "diabetes"

def anemia_severity(hb_value, sex='any'):
    v = safe_float(hb_value)
    if v is None:
        return None
    # conservative ranges
    if sex and sex.lower() == 'male':
        if v < 8: return "severe"
        if v < 11: return "moderate"
        if v < 13: return "mild"
        return "normal"
    else:
        # female/any default
        if v < 8: return "severe"
        if v < 11: return "moderate"
        if v < 12: return "mild"
        return "normal"

# ----------------- Main: read week2 JSONs, aggregate, produce summary -----------------
def load_parsed_reports(folder: Path):
    reports = []
    for f in sorted(folder.glob('*.json')):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            # canonicalize structure: many week2 files use keys 'parsed' or top-level params
            if isinstance(data, dict):
                if 'interpreted' in data and 'parsed' in data:
                    row = {**data.get('parsed', {}), **data.get('interpreted', {})}
                    # keep some metadata
                    meta = {"source_file": data.get('file', f.name)}
                else:
                    row = data
                    meta = {"source_file": f.name}
                reports.append({"file": f.name, "data": row, "meta": meta})
        except Exception as e:
            print(f"[WARN] Could not load {f.name}: {e}")
    return reports

def compute_week3_summary(reports):
    # iterate reports, extract parameters: hemoglobin, glucose, cholesterol, platelet_count, rbc_count
    items = []
    for r in reports:
        d = r['data']
        # d may be nested: try top-level keys and/or values inside nested dicts
        def get_param(key):
            # common patterns: value stored as dict with 'value_standard' or 'value_raw'
            if key in d:
                v = d[key]
                if isinstance(v, dict):
                    return v.get('value_standard') or v.get('value_raw') or None
                return v
            # sometimes interpreted keys exist
            if 'interpreted' in d and isinstance(d['interpreted'], dict):
                v = d['interpreted'].get(key)
                if isinstance(v, dict):
                    return v.get('value_standard') or v.get('value_raw') or None
            # fallback: search nested dicts for key substring
            for k2,v2 in d.items():
                if isinstance(k2, str) and key in k2.lower():
                    if isinstance(v2, dict):
                        return v2.get('value_standard') or v2.get('value_raw') or None
                    return v2
            return None

        hb = get_param('hemoglobin')
        glucose = get_param('glucose')
        chol = get_param('cholesterol') or get_param('total_cholesterol') or get_param('ldl') or get_param('hdl')
        platelet = get_param('platelet_count') or get_param('platelet')
        rbc = get_param('rbc') or get_param('rbc_count') or get_param('red_blood_cell')

        items.append({
            "file": r['file'],
            "hemoglobin": hb,
            "glucose": glucose,
            "cholesterol": chol,
            "platelet_count": platelet,
            "rbc_count": rbc
        })

    # build aggregate summary
    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "reports_count": len(items),
        "reports": items,
        "computed_patterns": [],
        "risk_scores": {},
        "overall_health_flag": None,
        "notes": "Automated week-3 summary. This is not a medical diagnosis."
    }

    # compute simple population stats for hemoglobin / glucose / cholesterol
    def collect_vals(key):
        vals = []
        for it in items:
            v = safe_float(it.get(key))
            if v is not None:
                vals.append(v)
        return vals

    hb_vals = collect_vals("hemoglobin")
    g_vals = collect_vals("glucose")
    c_vals = collect_vals("cholesterol")

    if hb_vals:
        summary['hb_median'] = statistics.median(hb_vals)
    if g_vals:
        summary['glucose_median'] = statistics.median(g_vals)
    if c_vals:
        summary['cholesterol_median'] = statistics.median(c_vals)

    # detect simple patterns per-report
    patterns = []
    ch_ratios = []
    for it in items:
        ch = it.get('cholesterol')
        hb = it.get('hemoglobin')
        g = it.get('glucose')
        # compute cholesterol ratio if possible (total/hdl) — best-effort
        ratio = cholesterol_ratio(ch)  # this will likely be None without HDL present
        if ratio:
            ch_ratios.append(ratio)
            if ratio > 5.0:
                patterns.append(f"High cholesterol ratio detected in {it['file']} (ratio {ratio})")
        # anemia pattern
        an = anemia_severity(hb)
        if an and an != "normal":
            patterns.append(f"Anemia ({an}) suggested by hemoglobin {hb} in {it['file']}")
        # glucose pattern
        gcat = glucose_category(g)
        if gcat and gcat != "normal":
            patterns.append(f"Glucose risk {gcat} in {it['file']} (value {g})")

    summary['computed_patterns'] = patterns

    # aggregate cholesterol ratio if we have some
    if ch_ratios:
        summary['risk_scores']['cholesterol_ratio_median'] = round(statistics.median(ch_ratios), 2)
        # categorize
        med = summary['risk_scores']['cholesterol_ratio_median']
        if med < 3.5:
            summary['risk_scores']['cholesterol_ratio_level'] = "good"
        elif med < 5.0:
            summary['risk_scores']['cholesterol_ratio_level'] = "moderate"
        else:
            summary['risk_scores']['cholesterol_ratio_level'] = "high"

    # simple glucose risk aggregation
    if g_vals:
        high_count = sum(1 for v in g_vals if v >= 126)
        pre_count = sum(1 for v in g_vals if 100 <= v < 126)
        summary['risk_scores']['glucose_counts'] = {"diabetes": high_count, "prediabetes": pre_count, "normal": len(g_vals) - (high_count + pre_count)}

    # overall health flag: naive heuristic
    risk_points = 0
    if summary['risk_scores'].get('cholesterol_ratio_level') == 'high':
        risk_points += 2
    if summary['risk_scores'].get('glucose_counts', {}).get('diabetes', 0) > 0:
        risk_points += 2
    if any('Anemia' in p for p in patterns):
        risk_points += 1

    if risk_points >= 3:
        summary['overall_health_flag'] = "high-risk"
    elif risk_points == 2:
        summary['overall_health_flag'] = "moderate-risk"
    else:
        summary['overall_health_flag'] = "low-risk"

    return summary

def save_summary(summary, out_folder: Path):
    out_folder.mkdir(parents=True, exist_ok=True)
    out_path = out_folder / "week3_summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print("Saved week3 summary to:", out_path.resolve())

# ----------------- Run flow -----------------
def main():
    cfg = load_config()
    repo_root = Path(cfg.get('repo_root', '.')).resolve()
    print("Repo root:", repo_root)
    week2_folder = find_week2_json_folder(cfg)
    print("Using Week-2 JSON folder:", week2_folder)

    reports = load_parsed_reports(week2_folder)
    print(f"Loaded {len(reports)} parsed JSON reports from Week-2.")

    summary = compute_week3_summary(reports)
    out_folder = (repo_root / cfg.get('week3_output', 'Mahesh/Week3/output/week3_analysis')).resolve()
    save_summary(summary, out_folder)
    print("Done. Summary overall flag:", summary.get('overall_health_flag'))

if __name__ == "__main__":
    main()
