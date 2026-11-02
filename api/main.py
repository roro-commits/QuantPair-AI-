"""QuantPairs API — read-only dashboard over the pipeline outputs. Never calls model.predict().

Run: pdm run uvicorn api.main:app --reload
"""
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

ROOT = Path(__file__).resolve().parents[1]
TABLES = {
    "pairs": ROOT / "cointegration_output/cointegration_results.csv",
    "locked": ROOT / "cointegration_output/locked_pairs.csv",
    "performance": ROOT / "strategy_output/performance.csv",
    "signals": ROOT / "strategy_output/signals.csv",
    "model": ROOT / "model_output/model_comparison.csv",
    "sentiment": ROOT / "sentiment_output/sentiment.csv",
}

app = FastAPI(title="QuantPairs", description="Pair trading analytics — reporting only")


def read_table(name: str) -> pd.DataFrame:
    """Load one output table or 404."""
    path = TABLES.get(name)
    if path is None or not path.exists():
        raise HTTPException(404, f"unknown or missing table: {name}")
    return pd.read_csv(path)


@app.get("/")
def index() -> dict:
    return {"endpoints": [f"/{k}" for k in TABLES] + ["/dashboard"]}


@app.get("/pairs")
def pairs() -> list:
    return read_table("pairs").to_dict(orient="records")


@app.get("/locked")
def locked() -> list:
    return read_table("locked").to_dict(orient="records")


@app.get("/performance")
def performance() -> list:
    return read_table("performance").to_dict(orient="records")


@app.get("/signals")
def signals(last: int = 20) -> list:
    return read_table("signals").tail(last).to_dict(orient="records")


@app.get("/model")
def model() -> list:
    return read_table("model").to_dict(orient="records")


@app.get("/sentiment")
def sentiment() -> list:
    return read_table("sentiment").to_dict(orient="records")


# ---------- dashboard rendering (presentation only, no analysis) ----------

STYLE = """
:root {
  color-scheme: light;
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e;
  --muted: #898781; --grid: #e1e0d9; --axis: #c3c2b7;
  --border: rgba(11,11,11,0.10); --series: #2a78d6;
  --up: #006300; --down: #d03b3b; --good: #0ca30c; --bad: #d03b3b;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink-2: #c3c2b7;
    --muted: #898781; --grid: #2c2c2a; --axis: #383835;
    --border: rgba(255,255,255,0.10); --series: #3987e5;
    --up: #0ca30c; --down: #e66767; --good: #0ca30c; --bad: #e66767;
  }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--page); color:var(--ink);
  font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif; }
.wrap { max-width:1020px; margin:0 auto; padding:28px 20px 64px; }
header h1 { font-size:22px; margin:0; }
header .sub { color:var(--ink-2); font-size:13px; margin-top:4px; }
.chip { display:inline-block; border:1px solid var(--border); border-radius:999px;
  padding:1px 10px; font-size:12px; color:var(--ink-2); background:var(--surface); }
.tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:12px; margin:22px 0; }
.tile { background:var(--surface); border:1px solid var(--border);
  border-radius:10px; padding:14px 16px; }
.tile .k { font-size:12px; color:var(--muted); }
.tile .v { font-size:26px; font-weight:650; margin-top:2px; }
.card { background:var(--surface); border:1px solid var(--border);
  border-radius:10px; padding:18px 20px; margin:16px 0; }
.card h2 { font-size:14px; margin:0 0 10px; color:var(--ink-2);
  font-weight:600; text-transform:uppercase; letter-spacing:.04em; }
table { border-collapse:collapse; width:100%; font-size:13.5px; }
th { text-align:right; color:var(--muted); font-weight:500; padding:6px 10px;
  border-bottom:1px solid var(--grid); }
th:first-child, td:first-child { text-align:left; }
td { text-align:right; padding:6px 10px; border-bottom:1px solid var(--grid);
  font-variant-numeric: tabular-nums; }
tr:last-child td { border-bottom:none; }
.pos { color:var(--up); } .neg { color:var(--down); }
.badge { display:inline-block; border-radius:999px; padding:0 9px; font-size:12px;
  border:1px solid var(--border); color:var(--ink-2); }
.badge.good { color:#fff; background:var(--good); border-color:transparent; }
.badge.bad  { color:#fff; background:var(--bad);  border-color:transparent; }
svg text { font:11px system-ui,sans-serif; fill:var(--muted); }
#tip { position:fixed; pointer-events:none; display:none; background:var(--surface);
  border:1px solid var(--border); border-radius:6px; padding:4px 8px;
  font-size:12px; color:var(--ink); box-shadow:0 2px 8px rgba(0,0,0,.12); }
footer { color:var(--muted); font-size:12px; margin-top:28px; }
"""

TIP_JS = """
const pts = %s;
const svg = document.getElementById('zchart');
const zdot = document.getElementById('zdot');
const tip = document.getElementById('tip');
svg.addEventListener('mousemove', e => {
  const r = svg.getBoundingClientRect();
  const fx = (e.clientX - r.left) / r.width * %d;
  let i = Math.max(0, Math.min(pts.length - 1, Math.round((fx - %d) / %f)));
  const [x, y, d, z] = pts[i];
  zdot.setAttribute('cx', x); zdot.setAttribute('cy', y); zdot.style.display = 'block';
  tip.style.display = 'block'; tip.style.left = (e.clientX + 12) + 'px';
  tip.style.top = (e.clientY - 10) + 'px';
  tip.textContent = d + '  z = ' + z.toFixed(2);
});
svg.addEventListener('mouseleave', () => { zdot.style.display = 'none'; tip.style.display = 'none'; });
"""


def fmt(v, kind: str = "num") -> str:
    """Format one value for the dashboard."""
    if kind == "pct":
        return f"{v:+.1f}%"
    if kind == "num2":
        return f"{v:.2f}"
    return f"{v}"


def cell(col: str, v, signed: set) -> str:
    """One <td>, coloring signed numerics and badging labels/flags."""
    if col == "tradeable":
        return f'<td><span class="badge {"good" if v else ""}">{"pass" if v else "fail"}</span></td>'
    if col == "label":
        cls = {"positive": "good", "negative": "bad"}.get(str(v), "")
        return f'<td><span class="badge {cls}">{v}</span></td>'
    if col in signed and isinstance(v, (int, float)):
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f'<td class="{cls}">{v}</td>'
    return f"<td>{v}</td>"


def render_table(df: pd.DataFrame, signed: set = frozenset()) -> str:
    """DataFrame -> styled HTML table."""
    head = "".join(f"<th>{c.replace('_', ' ')}</th>" for c in df.columns)
    rows = "".join(
        "<tr>" + "".join(cell(c, r[c], signed) for c in df.columns) + "</tr>"
        for _, r in df.iterrows()
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>"


def zscore_svg(sig: pd.DataFrame, last: int = 250) -> tuple:
    """Z-score line with entry/exit threshold bands. Returns (svg, tooltip js)."""
    import json

    sig = sig.dropna(subset=["z"]).tail(last)
    w, h, left, right, top, bot = 960, 240, 46, 70, 14, 22
    zmax = 3.0
    xs = left + (w - left - right) * pd.Series(range(len(sig))) / max(len(sig) - 1, 1)
    step = (w - left - right) / max(len(sig) - 1, 1)
    y = lambda z: top + (h - top - bot) * (zmax - max(min(z, zmax), -zmax)) / (2 * zmax)
    pts = " ".join(f"{x:.1f},{y(z):.1f}" for x, z in zip(xs, sig["z"]))
    data = [[round(x, 1), round(y(z), 1), str(d)[:10], round(z, 3)]
            for x, z, d in zip(xs, sig["z"], sig["Date"])]

    def hline(z, label, dash="4 4"):
        yy = y(z)
        return (f'<line x1="{left}" y1="{yy:.1f}" x2="{w-right}" y2="{yy:.1f}" '
                f'stroke="var(--grid)" stroke-dasharray="{dash}"/>'
                f'<text x="{w-right+6}" y="{yy+4:.1f}">{label}</text>')

    svg = f"""<svg id="zchart" viewBox="0 0 {w} {h}" width="100%" role="img"
  aria-label="Rolling z-score of the ratio difference, last {len(sig)} trading days">
  {hline(1.5, "+1.5 entry")}{hline(-1.5, "−1.5 entry")}
  {hline(0.5, "+0.5 exit", "2 5")}{hline(-0.5, "−0.5 exit", "2 5")}
  <line x1="{left}" y1="{y(0):.1f}" x2="{w-right}" y2="{y(0):.1f}" stroke="var(--axis)"/>
  <text x="{w-right+6}" y="{y(0)+4:.1f}">0</text>
  <polyline points="{pts}" fill="none" stroke="var(--series)" stroke-width="2"
    stroke-linejoin="round" stroke-linecap="round"/>
  <circle id="zdot" r="4" fill="var(--series)" stroke="var(--surface)"
    stroke-width="2" style="display:none"/>
  <text x="{left}" y="{h-4}">{data[0][2]}</text>
  <text x="{w-right}" y="{h-4}" text-anchor="end">{data[-1][2]}</text>
</svg>"""
    js = TIP_JS % (json.dumps(data), w, left, step)
    return svg, js


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    """One-page view: KPIs, z-score chart, pairs, P&L, model, sentiment, signals."""
    perf = read_table("performance")
    full = perf[perf["window"] == "full"].iloc[0]
    lock = read_table("locked").iloc[0]
    sig = read_table("signals")
    sent = read_table("sentiment")

    sign = lambda v: "pos" if v > 0 else "neg" if v < 0 else ""
    tiles = "".join(
        f'<div class="tile"><div class="k">{k}</div><div class="v {cls}">{v}</div></div>'
        for k, v, cls in [
            ("Cumulative return", fmt(full["cumulative_return_pct"], "pct"), sign(full["cumulative_return_pct"])),
            ("Sharpe", fmt(full["sharpe"], "num2"), sign(full["sharpe"])),
            ("Max drawdown", fmt(full["max_drawdown_pct"], "pct"), sign(full["max_drawdown_pct"])),
            ("Trades", int(full["trades"]), ""),
            ("Days in market", f'{full["days_in_market_pct"]:.0f}%', ""),
        ]
    )

    svg, tip_js = zscore_svg(sig)
    signed = {"cumulative_return_pct", "sharpe", "max_drawdown_pct",
              "strategy_return", "p1_change", "mean_score", "z"}

    cards = f"""
<div class="card"><h2>Z-score — ratio difference (last 250 days)</h2>{svg}</div>
<div class="card"><h2>Cointegration screen — locked pair</h2>{render_table(read_table("pairs").round(4), signed)}</div>
<div class="card"><h2>Strategy performance (Altucher unilateral, {lock['y']}/{lock['x']})</h2>{render_table(perf.round(2), signed)}</div>
<div class="card"><h2>Model comparison — vs baselines</h2>{render_table(read_table("model").round(4), signed)}</div>
<div class="card"><h2>Sentiment — display only, never gates trading</h2>{render_table(sent.round(3), signed)}</div>
<div class="card"><h2>Latest signals</h2>{render_table(sig.tail(10).round(4), signed)}</div>"""

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>QuantPairs</title><style>{STYLE}</style></head><body><div class="wrap">
<header><h1>QuantPairs — Pair Trading Dashboard</h1>
<div class="sub">Locked pair <span class="chip">{lock['y']} / {lock['x']}</span>
&nbsp;β = {lock['beta']:.2f} &nbsp;·&nbsp; coint p = {lock['coint_p']:.4f}
&nbsp;·&nbsp; half-life ≈ {lock['half_life']:.0f}d &nbsp;·&nbsp; reporting only — no live predictions</div>
</header>
<div class="tiles">{tiles}</div>
{cards}
<footer>QuantPairs · data 2018–2025 via yfinance · sentiment as of {sent['as_of'].iloc[0][:10]}</footer>
</div><div id="tip"></div><script>{tip_js}</script></body></html>"""
