#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a minimal static index.html for GitHub Pages.

- Lists schematic figures (PNG/JPG/SVG/WebP) under figures/schematics/
- Lists MP4 videos under videos/
- Lists MATLAB .m files under src/
- Builds an "Overview" section pairing the Two/Three schematics with the
  corresponding videos when available.
- Writes assets/style.css and .nojekyll to keep Pages simple.

CI-safe: even if something goes wrong, still writes index.html with logs.
"""

import os
import re
import sys
import traceback
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

# ---------- Repository metadata (injected by GitHub Actions; local defaults) ----------
REPO_FULL = os.getenv("GITHUB_REPOSITORY", "kl543/rydberg-atoms-simulation-")  # user/repo
BRANCH    = os.getenv("GITHUB_REF_NAME", "main")
OWNER, REPO_NAME = (REPO_FULL.split("/", 1) + [""])[:2]

# ---------- Paths ----------
ROOT     = Path(__file__).resolve().parents[1]   # repo root
OUT_HTML = ROOT / "index.html"
ASSETS   = ROOT / "assets"
FIG_DIR  = ROOT / "figures" / "schematics"
VID_DIR  = ROOT / "videos"
SRC_DIR  = ROOT / "src"

def _q(p: Path | str) -> str:
    """URL-encode a path but keep slashes and common filename chars."""
    if isinstance(p, Path):
        p = p.as_posix()
    return quote(p, safe="/-._")

def _h(s: str) -> str:
    """Basic HTML escape."""
    return (s.replace("&","&amp;")
             .replace("<","&lt;")
             .replace(">","&gt;")
             .replace('"',"&quot;"))

def _log_env():
    print(f"[env] REPO_FULL={REPO_FULL} BRANCH={BRANCH}")
    print(f"[env] ROOT={ROOT}")
    for d in (FIG_DIR, VID_DIR, SRC_DIR):
        print(f"[scan] {d} exists? {d.exists()}")

def _ensure_assets():
    """Create assets dir, a minimal stylesheet, and .nojekyll."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    (ASSETS / "style.css").write_text("""
html,body{margin:0;padding:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.6;color:#111;background:#fff}
header{background:#111;color:#fff;padding:30px 16px;text-align:center}
.container{max-width:1040px;margin:24px auto;padding:0 16px}
.muted{color:#666}
.card{border:1px solid #e9e9e9;border-radius:16px;padding:16px 18px;margin:16px 0;background:#fff}

/* Grid for the Schematics section */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.thumb{border:1px solid #e9e9e9;border-radius:12px;padding:6px;background:#fff}
.thumb img{width:100%;height:auto;border-radius:8px;display:block}

.btn{display:inline-block;border:1px solid #e9e9e9;padding:8px 12px;border-radius:10px;text-decoration:none;color:#111;background:#fafafa}
.btn:hover{background:#f3f3f3}

video.player{width:100%;height:auto;border:1px solid #e9e9e9;border-radius:12px;background:#000}
.center{text-align:center}
h2{margin:18px 0 10px}
h3{margin:.2rem 0 .5rem}

/* --- shrink big media (Overview & Videos) --- */
/* Limit width and center for non-grid media */
.card > .thumb{
  max-width: clamp(320px, 90vw, 760px);
  margin:12px auto;
}
video.player{
  max-width: clamp(320px, 90vw, 760px);
  display:block;
  margin:12px auto;
}
/* In schematics grid, keep fluid tiles */
.grid .thumb{
  max-width:none;
  margin:0;
}
""".strip() + "\n", encoding="utf-8")

def _load_header() -> str:
    """Load a shared _site-header.html if present; otherwise use a fallback header."""
    for p in (ROOT / "_site-header.html", ROOT.parent / "_site-header.html"):
        if p.exists():
            print(f"[header] using {p}")
            return p.read_text(encoding="utf-8")
    print("[header] using fallback")
    return """<!doctype html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Rydberg Polaritons — Relative-Phase Dynamics</title>
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header>
  <h1>Rydberg Polaritons — Relative-Phase Dynamics</h1>
  <div class="muted">MATLAB scripts • schematic figures • MP4 clips</div>
</header>
"""

# ---------- Enumerators ----------
def _key_from_filename(name: str) -> str | None:
    """Classify by 'two' / 'three' keyword in filename for pairing."""
    n = name.lower()
    if re.search(r"\bthree\b", n): return "three"
    if re.search(r"\btwo\b", n):   return "two"
    return None

def _list_figs() -> list[str]:
    if not FIG_DIR.exists():
        return []
    exts = {".png", ".svg", ".jpg", ".jpeg", ".webp"}
    items = [p for p in FIG_DIR.iterdir() if p.is_file() and p.suffix.lower() in exts]
    items.sort(key=lambda p: p.name.lower())
    print(f"[figs] {len(items)} files")
    return [p.relative_to(ROOT).as_posix() for p in items]

def _list_vids() -> list[str]:
    if not VID_DIR.exists():
        return []
    items = sorted(VID_DIR.glob("*.mp4"), key=lambda p: p.name.lower())
    print(f"[vids] {len(items)} files")
    return [p.relative_to(ROOT).as_posix() for p in items]

def _list_src() -> list[str]:
    if not SRC_DIR.exists():
        return []
    items = [p for p in SRC_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".m"]
    items.sort(key=lambda p: p.name.lower())
    print(f"[src] {len(items)} MATLAB .m files")
    return [p.relative_to(ROOT).as_posix() for p in items]

def _pair_overview(figs: list[str], vids: list[str]) -> list[dict]:
    """Build Two/Three overview cards from file names."""
    f, v = {}, {}
    for rel in figs:
        k = _key_from_filename(Path(rel).name)
        if k and k not in f:
            f[k] = rel
    for rel in vids:
        k = _key_from_filename(Path(rel).name)
        if k and k not in v:
            v[k] = rel
    print(f"[pair] figs={f} vids={v}")
    items = []
    for k in ("two", "three"):
        if k not in f and k not in v:
            continue
        if k == "two":
            title = "Two Rydberg Polaritons — Relative-Phase Evolution"
            cap   = "Relative phase Δϕ(t) for two polaritons; each has blockade radius R_b."
        else:
            title = "Three Rydberg Polaritons — Relative-Phase Evolution"
            cap   = "Pairwise phases Δϕ₁₂, Δϕ₂₃, Δϕ₃₁ (mod 2π) during propagation."
        items.append({"title": title, "fig": f.get(k, ""), "vid": v.get(k, ""), "cap": cap})
    return items

# ---------- HTML sections ----------
def _sec_overview(items: list[dict]) -> str:
    if not items:
        return '<section class="card"><h2>Overview</h2><div class="muted">No Two/Three items found.</div></section>'
    parts = ['<section class="card"><h2>Overview</h2>']
    for it in items:
        title = _h(it["title"])
        fig = f'<div class="thumb"><img src="{_q(it["fig"])}" alt="{title} schematic" loading="lazy"></div>' if it["fig"] else ""
        vid = f'<video class="player" controls preload="metadata" src="{_q(it["vid"])}"></video>' if it["vid"] else ""
        parts.append(f"<h3>{title}</h3>{fig}{vid}<p class='muted'>{_h(it['cap'])}</p>")
    parts.append("</section>")
    return "\n".join(parts)

def _sec_list(title: str, items: list[str], kind: str) -> str:
    """kind: 'grid' for images, 'videos' for mp4, 'list' for links."""
    html = [f'<section class="card"><h2>{_h(title)}</h2>']
    if not items:
        html.append('<div class="muted">None.</div>')
    else:
        if kind == "grid":
            html.append('<div class="grid">')
            for rel in items:
                name = _h(Path(rel).name)
                html.append(
                    f'<a class="thumb" href="{_q(rel)}" target="_blank" rel="noreferrer">'
                    f'<img src="{_q(rel)}" alt="{name}" loading="lazy"></a>'
                )
            html.append('</div>')
        elif kind == "videos":
            for rel in items:
                name = _h(Path(rel).name)
                html.append(
                    f'<div style="margin:10px 0 18px"><b>{name}</b><br>'
                    f'<video class="player" controls preload="metadata" src="{_q(rel)}"></video></div>'
                )
        elif kind == "list":
            html.append('<ul style="margin:6px 0 0 18px">')
            for rel in items:
                name = _h(Path(rel).name)
                html.append(f'<li><a class="btn" href="{_q(rel)}">{name}</a></li>')
            html.append('</ul>')
    html.append('</section>')
    return "\n".join(html)

# ---------- Build HTML ----------
def _build_ok() -> str:
    header = _load_header()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    figs  = _list_figs()
    vids  = _list_vids()
    srcs  = _list_src()
    pairs = _pair_overview(figs, vids)

    # --- collect files used in Overview to avoid duplicates later ---
    used_figs = {it["fig"] for it in pairs if it.get("fig")}
    used_vids = {it["vid"] for it in pairs if it.get("vid")}
    figs_rest = [p for p in figs if p not in used_figs]
    vids_rest = [p for p in vids if p not in used_vids]

    out = [header, '<main class="container">']
    # Overview (always if available)
    if pairs:
        out.append(_sec_overview(pairs))
    # Only show remaining items; skip empty sections to avoid duplication
    if figs_rest:
        out.append(_sec_list("Schematics", figs_rest, "grid"))
    if vids_rest:
        out.append(_sec_list("Videos", vids_rest, "videos"))
    # MATLAB sources are unique anyway
    if srcs:
        out.append(_sec_list("Source Code (MATLAB, src/)", srcs, "list"))

    out.append(f'<div class="center muted" style="margin:24px 0;">Last updated: {now} — {OWNER}/{REPO_NAME}@{BRANCH}</div>')
    out.append('</main></body></html>')
    return "\n".join(out)

def _build_error(err_html: str) -> str:
    header = _load_header()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""{header}
<main class="container">
  <section class="card">
    <h2>Build Error</h2>
    <div class="muted">An error occurred while generating this page. Logs from CI:</div>
    <pre style="white-space:pre-wrap">{err_html}</pre>
  </section>
  <div class="center muted" style="margin:24px 0;">Last updated: {now} — {OWNER}/{REPO_NAME}@{BRANCH}</div>
</main></body></html>"""

def main():
    try:
        print("[gen] start")
        _log_env()
        _ensure_assets()
        html = _build_ok()
        OUT_HTML.write_text(html, encoding="utf-8")
        print(f"[gen] wrote {OUT_HTML}")
    except Exception:
        tb = traceback.format_exc()
        print("[gen][ERROR]\n" + tb, file=sys.stderr)
        OUT_HTML.write_text(_build_error(_h(tb)), encoding="utf-8")
        print("[gen] error page written")

if __name__ == "__main__":
    main()
