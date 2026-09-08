from __future__ import annotations

import json
import html as html_lib
from pathlib import Path
from typing import Any

import pandas as pd


def _read_csv(path: Path, required: list[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    if required and not all(c in frame.columns for c in required):
        return pd.DataFrame()
    return frame


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def _json_script(data: Any) -> str:
    # Prevent an accidental </script> sequence inside data from terminating the tag.
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def _safe_text(value: Any) -> str:
    return html_lib.escape("" if pd.isna(value) else str(value))


def build_dashboard(results_root: str | Path, output_path: str | Path) -> Path:
    """Build a dependency-free interactive HTML dashboard from final reporting artifacts."""
    root = Path(results_root)
    final = root / "final" / "dashboard_data"
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    overview = _read_csv(final / "dataset_overview.csv")
    quality = _read_csv(final / "quality_summary.csv")
    classes = _read_csv(final / "class_distribution.csv")
    per_file = _read_csv(final / "class_distribution_by_file.csv")
    metrics = _read_csv(final / "ml_metrics.csv")
    per_class = _read_csv(final / "ml_per_class_metrics.csv")
    importance = _read_csv(final / "ml_feature_importance.csv")
    decision = _read_csv(final / "final_dataset_selection.csv")
    comparison = _read_csv(root / "cross_dataset_comparison" / "dataset_comparison_matrix.csv")
    confusion = _read_csv(final / "ml_confusion_matrix.csv")

    # Prefer final ML results; baseline results are supplementary and should not
    # silently replace the final evaluation in the dashboard.
    if metrics.empty:
        metrics = _read_csv(root / "ml_baseline" / "model_comparison.csv")

    model = metrics.iloc[0].to_dict() if not metrics.empty else {}
    selected_dataset = "CIC-IDS2017"
    if not decision.empty:
        if {"dataset", "role", "decision"}.issubset(decision.columns):
            row = decision[decision["role"].astype(str).str.lower().eq("primary")]
            if not row.empty:
                selected_dataset = str(row.iloc[0]["dataset"])
        elif "selection" in decision.columns and "decision_item" in decision.columns:
            row = decision[decision["decision_item"].astype(str).str.lower().eq("primary dataset")]
            if not row.empty:
                selected_dataset = str(row.iloc[0]["selection"])

    kpis = {
        "dataset": selected_dataset,
        "classes": int(model.get("classes", classes["label"].nunique() if "label" in classes else 0) or 0),
        "features": int(model.get("features", 0) or 0),
        "accuracy": float(model.get("accuracy", 0) or 0),
        "balanced_accuracy": float(model.get("balanced_accuracy", 0) or 0),
        "macro_f1": float(model.get("macro_f1", 0) or 0),
        "weighted_f1": float(model.get("weighted_f1", 0) or 0),
    }

    payload = {
        "kpis": kpis,
        "overview": _records(overview),
        "quality": _records(quality),
        "classes": _records(classes),
        "per_file": _records(per_file),
        "metrics": _records(metrics),
        "per_class": _records(per_class),
        "importance": _records(importance),
        "decision": _records(decision),
        "comparison": _records(comparison),
        "confusion": _records(confusion),
    }

    title = "CIC Dataset Analysis — Final Dashboard"
    document = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{ --bg:#f5f7fa; --panel:#fff; --ink:#172033; --muted:#687386; --line:#dfe4ec; --accent:#315efb; --good:#16835b; --warn:#b7791f; }}
* {{ box-sizing:border-box }} body {{ margin:0; font-family:Inter,Segoe UI,Arial,sans-serif; background:var(--bg); color:var(--ink) }}
header {{ padding:28px 34px 20px; background:var(--panel); border-bottom:1px solid var(--line) }}
h1 {{ margin:0 0 6px; font-size:28px }} header p {{ margin:0;color:var(--muted) }}
nav {{ display:flex; gap:8px; padding:12px 34px; background:#fff; border-bottom:1px solid var(--line); position:sticky;top:0;z-index:3;overflow:auto }}
nav button {{ border:0;background:transparent;padding:9px 13px;border-radius:8px;cursor:pointer;color:var(--muted);font-weight:600;white-space:nowrap }}
nav button.active, nav button:hover {{ background:#edf1ff;color:var(--accent) }}
main {{ max-width:1400px;margin:auto;padding:26px 30px 60px }}
.page {{ display:none }} .page.active {{ display:block }}
.grid {{ display:grid;gap:18px }} .kpis {{ grid-template-columns:repeat(7,minmax(0,1fr)) }} .two {{ grid-template-columns:repeat(2,minmax(0,1fr)) }}
.card {{ background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px;box-shadow:0 2px 8px rgba(20,30,50,.04) }}
.kpi .label {{ color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.05em }} .kpi .value {{ font-size:25px;font-weight:750;margin-top:8px }}
h2 {{ font-size:19px;margin:0 0 14px }} h3 {{ font-size:15px;margin:18px 0 10px }}
.small {{ color:var(--muted);font-size:13px }}
.bar-row {{ display:grid;grid-template-columns:minmax(170px,1.4fr) 4fr 90px;gap:10px;align-items:center;margin:7px 0;font-size:13px }}
.bar {{ height:12px;background:#edf0f5;border-radius:99px;overflow:hidden }} .bar > span {{ display:block;height:100%;background:var(--accent);border-radius:99px }}
.metric-row {{ display:grid;grid-template-columns:1.5fr 3fr 80px;gap:10px;align-items:center;margin:9px 0 }}
table {{ width:100%;border-collapse:collapse;font-size:13px }} th,td {{ padding:8px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top }} th {{ background:#f8f9fb;position:sticky;top:0 }}
.table-wrap {{ max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:8px }}
.heatmap {{ display:grid;grid-template-columns:repeat(15,minmax(32px,1fr));gap:2px;overflow:auto }} .cell {{ min-height:32px;display:flex;align-items:center;justify-content:center;font-size:9px;border-radius:2px }}
.callout {{ border-left:4px solid var(--accent);background:#f4f6ff;padding:14px 16px;border-radius:7px }}
@media(max-width:1000px) {{ .kpis{{grid-template-columns:repeat(3,1fr)}} .two{{grid-template-columns:1fr}} }}
@media(max-width:600px) {{ .kpis{{grid-template-columns:repeat(2,1fr)}} main{{padding:18px 12px}} header{{padding:22px 16px}} nav{{padding-left:12px}} }}
</style>
</head>
<body>
<header><h1>{title}</h1><p>Artifact-driven view of the completed CIC dataset analysis, final dataset decision, and ML evaluation.</p></header>
<nav id="nav">
<button class="active" data-page="overview">Overview</button><button data-page="quality">Data Quality</button><button data-page="classes">Classes</button><button data-page="ml">ML Performance</button><button data-page="features">Features</button><button data-page="decision">Final Decision</button>
</nav>
<main>
<section id="overview" class="page active">
<div class="grid kpis" id="kpis"></div>
<div class="grid two" style="margin-top:18px"><div class="card"><h2>Project snapshot</h2><div id="snapshot"></div></div><div class="card"><h2>Model result</h2><div id="model-summary"></div></div></div>
</section>
<section id="quality" class="page"><div class="grid two"><div class="card"><h2>Dataset quality</h2><div id="quality-table"></div></div><div class="card"><h2>Cross-dataset comparison</h2><div id="comparison-table"></div></div></div></section>
<section id="classes" class="page"><div class="card"><h2>Class distribution</h2><div id="class-bars"></div></div><div class="card" style="margin-top:18px"><h2>Per-source class distribution</h2><div class="table-wrap"><div id="per-file-table"></div></div></div></section>
<section id="ml" class="page"><div class="card"><h2>Model metrics</h2><div id="metrics"></div></div><div class="grid two" style="margin-top:18px"><div class="card"><h2>Per-class performance</h2><div class="table-wrap"><div id="per-class"></div></div></div><div class="card"><h2>Confusion matrix</h2><div id="confusion" class="table-wrap"></div></div></div></section>
<section id="features" class="page"><div class="card"><h2>Random Forest feature importance</h2><div id="importance"></div></div></section>
<section id="decision" class="page"><div class="card"><h2>Final dataset selection</h2><div id="decision-table"></div></div></section>
</main>
<script>
const DATA = {_json_script(payload)};
const $ = id => document.getElementById(id);
const fmt = (x,d=3) => Number(x).toLocaleString(undefined,{{maximumFractionDigits:d}});
const pct = x => (Number(x)*100).toFixed(2)+'%';
const clean = s => String(s ?? '').replaceAll('�','–');
function table(rows, columns) {{
 if(!rows.length) return '<p class="small">No artifact available.</p>';
 return '<table><thead><tr>'+columns.map(c=>'<th>'+clean(c)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+columns.map(c=>'<td>'+clean(r[c])+'</td>').join('')+'</tr>').join('')+'</tbody></table>';
}}
function render() {{
 const k=DATA.kpis;
 const cards=[['Dataset',k.dataset],['Classes',k.classes],['Features',k.features],['Accuracy',pct(k.accuracy)],['Balanced accuracy',pct(k.balanced_accuracy)],['Macro F1',pct(k.macro_f1)],['Weighted F1',pct(k.weighted_f1)]];
 $('kpis').innerHTML=cards.map(x=>'<div class="card kpi"><div class="label">'+x[0]+'</div><div class="value">'+clean(x[1])+'</div></div>').join('');
 $('snapshot').innerHTML='<p><b>Primary dataset:</b> '+clean(k.dataset)+'</p><p><b>Feature count:</b> '+k.features+'</p><p><b>Traffic classes:</b> '+k.classes+'</p><p class="small">Dashboard values are read from completed result artifacts; raw datasets are not reloaded.</p>';
 const m=DATA.metrics[0]||{{}}; $('model-summary').innerHTML='<p><b>Model:</b> '+clean(m.model)+'</p><p><b>Macro F1:</b> '+pct(m.macro_f1)+'</p><p><b>Balanced accuracy:</b> '+pct(m.balanced_accuracy)+'</p><p><b>Weighted F1:</b> '+pct(m.weighted_f1)+'</p>';
 $('quality-table').innerHTML=table(DATA.quality,Object.keys(DATA.quality[0]||{{}}));
 $('comparison-table').innerHTML=table(DATA.comparison,Object.keys(DATA.comparison[0]||{{}}));
 const cls=DATA.classes.slice().sort((a,b)=>Number(b.count)-Number(a.count)); const max=Math.max(...cls.map(x=>Number(x.count)||0),1);
 $('class-bars').innerHTML=cls.map(x=>'<div class="bar-row"><div>'+clean(x.label)+'</div><div class="bar"><span style="width:'+((Number(x.count)/max)*100).toFixed(2)+'%"></span></div><div>'+fmt(x.count,0)+' ('+fmt(x.percentage,2)+'%)</div></div>').join('');
 $('per-file-table').innerHTML=table(DATA.per_file,Object.keys(DATA.per_file[0]||{{}}));
 $('metrics').innerHTML=DATA.metrics.map(m=>'<div class="metric-row"><b>'+clean(m.model)+'</b><div class="bar"><span style="width:'+(Number(m.macro_f1)*100)+'%"></span></div><span>'+pct(m.macro_f1)+'</span></div>').join('');
 $('per-class').innerHTML=table(DATA.per_class,['class','precision','recall','f1','support']);
 const cm=DATA.confusion;
 if(cm.length) {{
   const cols=Object.keys(cm[0]);
   $('confusion').innerHTML=table(cm,cols);
 }} else {{ $('confusion').innerHTML='<p class="small">No confusion-matrix artifact available.</p>'; }}
 const imp=DATA.importance.slice().sort((a,b)=>Number(b.importance)-Number(a.importance)).slice(0,20); const imax=Math.max(...imp.map(x=>Number(x.importance)),1);
 $('importance').innerHTML=imp.map(x=>'<div class="bar-row"><div>'+clean(x.feature)+'</div><div class="bar"><span style="width:'+((Number(x.importance)/imax)*100).toFixed(2)+'%"></span></div><div>'+Number(x.importance).toFixed(4)+'</div></div>').join('');
 $('decision-table').innerHTML=table(DATA.decision,Object.keys(DATA.decision[0]||{{}}));
}}
document.querySelectorAll('#nav button').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('#nav button').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.page').forEach(x=>x.classList.remove('active'));b.classList.add('active');$(b.dataset.page).classList.add('active')}}));
render();
</script>
</body></html>'''
    out.write_text(document, encoding="utf-8")
    return out
