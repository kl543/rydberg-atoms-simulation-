#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, sys, traceback
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

# —— 仓库信息（CI 自动注入；本地运行用默认值）——
REPO_FULL = os.getenv("GITHUB_REPOSITORY", "kl543/rydberg-atoms-simulation-")
BRANCH    = os.getenv("GITHUB_REF_NAME", "main")
OWNER, REPO_NAME = (REPO_FULL.split("/", 1) + [""])[:2]

# —— 路径 —— 
ROOT     = Path(__file__).resolve().parents[1]
OUT_HTML = ROOT / "index.html"
ASSETS   = ROOT / "assets"
FIG_DIR  = ROOT / "figures" / "schematics"
VID_DIR  = ROOT / "videos"
SRC_DIR  = ROOT / "src"

MAIN_SITE    = "https://kl543.github.io"
PROJECTS_URL = f"{MAIN_SITE}/projects.html"

def q(p: Path | str) -> str:
    if isinstance(p, Path): p = p.as_posix()
    return quote(p, safe="/-._")

def h(s: str) -> str:
    return (s.replace("&","&amp;").replace("<","&lt;")
              .replace(">","&gt;").replace('"',"&quot;"))

def log_env():
    print(f"[env] REPO_FULL={REPO_FULL} BRANCH={BRANCH}")
    print(f"[env] ROOT={ROOT}")
    for d in [FIG_DIR, VID_DIR, SRC_DIR]:
        print(f"[scan] {d} exists? {d.exists()}")

def ensure_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    (ASSETS / "style.css").write_text("""
html,body{margin:0;padding:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.6;color:#111;background:#fff}
header{background:#111;color:#fff;padding:30px 16px;text-align:center}
.container{max-width:1040px;margin:24px auto;padding:0 16px}
.muted{color:#666}
.card{border:1px solid #e9e9e9;border-radius:16px;padding:16px 18px;margin:16px 0;background:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.thumb{border:1px solid #e9e9e9;border-radius:12px;padding:6px;background:#fff}
.thumb img{width:100%;border-radius:8px;display:block}
video.player{width:100%;height:auto;border:1px solid #e9e9e9;border-radius:12px;background:#000}
.center{text-align:center}
""".strip()+"\n", encoding="utf-8")

def load_header() -> str:
    # 可与 mbe3 共用 _site-header.html；没有就用内置
    for p in [ROOT / "_site-header.html", ROOT.parent / "_site-header.html"]:
        if p.exists():
            print(f"[header] using {p}")
            return p.read_text(encoding="utf-8")
    print("[header] using fallback")
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Rydberg Polaritons — Relative-Phase Dynamics — Kaiming Liu</title>
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header>
  <h1>Rydberg Polaritons — Relative-Phase Dynamics</h1>
  <div class="muted">Schematics & MP4 clips (Two / Three)</div>
  <div style="margin-top:6px"><a href="{PROJECTS_URL}" style="color:#fff;text-decoration:underline">Back to Projects</a></div>
</header>
"""

def key_from_name(name: str) -> str | None:
    n = name.lower()
    if re.search(r"\bthree\b", n): return "three"
    if re.search(r"\btwo\b", n):   return "two"
    return None

def list_figs() -> list[str]:
    if not FIG_DIR.exists(): return []
    exts = {".png",".svg",".jpg",".jpeg",".webp"}
    items = [p for p in FIG_DIR.iterdir() if p.is_file() and p.suffix.lower() in exts]
    items.sort(key=lambda p: p.name.lower())
    print(f"[figs] {len(items)} files")
    return [p.relative_to(ROOT).as_posix() for p in items]

def list_vids() -> list[str]:
    if not VID_DIR.exists(): return []
    items = sorted(VID_DIR.glob("*.mp4"), key=lambda p: p.name.lower())
    print(f"[vids] {len(items)} files")
    return [p.relative_to(ROOT).as_posix() for p in items]

def list_src() -> list[str]:
    if not SRC_DIR.exists(): return []
    items = [p for p in SRC_DIR.iterdir() if p.is_file() and p.suffix.lower() in {".m",".py"}]
    items.sort(key=lambda p: p.name.lower())
    print(f"[src] {len(items)} files")
    return [p.relative_to(ROOT).as_posix() for p in items]

def pair_two_three(figs, vids):
    f, v = {}, {}
    for rel in figs:
        k = key_from_name(Path(rel).name)
        if k and k not in f: f[k] = rel
    for rel in vids:
        k = key_from_name(Path(rel).name)
        if k and k not in v: v[k] = rel
    print(f"[pair] figs={f} vids={v}")
    items = []
    for k in ("two","three"):
        if k not in f and k not in v: continue
        if k == "two":
            title = "Two Rydberg Polaritons — Relative-Phase Evolution"
            cap   = "Relative phase Δϕ(t) for two polaritons; each has blockade radius R_b."
        else:
            title = "Three Rydberg Polaritons — Relative-Phase Evolution"
            cap   = "Pairwise phases Δϕ₁₂, Δϕ₂₃, Δϕ₃₁ (mod 2π) during propagation."
        items.append({"title":title,"fig":f.get(k,""),"vid":v.get(k,""),"cap":cap})
    return items

def section_pairs(items):
    if not items:
        return '<section class="card"><h2>Overview</h2><div class="muted">No items detected (“Two/Three”).</div></section>'
    parts = ['<section class="card"><h2>Overview</h2>']
    for it in items:
        title = h(it["title"])
        fig = f'<div class="thumb"><img src="{q(it["fig"])}" alt="{title} schematic" loading="lazy"></div>' if it["fig"] else ""
        vid = f'<video class="player" controls preload="metadata" src="{q(it["vid"])}"></video>' if it["vid"] else ""
        parts.append(f"<h3>{title}</h3>{fig}{vid}<p class='muted'>{h(it['cap'])}</p>")
    parts.append("</section>")
    return "\n".join(parts)

def section_list(title, paths, kind):
    html = [f'<section class="card"><h2>{h(title)}</h2>']
    if not paths:
        html.append('<div class="muted">None.</div>')
    else:
        if kind == "grid":
            html.append('<div class="grid">')
            for rel in paths:
                name = h(Path(rel).name)
                html.append(f'<a class="thumb" href="{q(rel)}" target="_blank" rel="noreferrer">'
                            f'<img src="{q(rel)}" alt="{name}" loading="lazy"></a>')
            html.append('</div>')
        elif kind == "videos":
            for rel in paths:
                name = h(Path(rel).name)
                html.append(f'<div style="margin:10px 0 18px"><b>{name}</b><br>'
                            f'<video class="player" controls preload="metadata" src="{q(rel)}"></video></div>')
        elif kind == "list":
            html.append('<ul style="margin:6px 0 0 18px">')
            for rel in paths:
                name = h(Path(rel).name)
                html.append(f'<li><a class="btn" href="{q(rel)}">{name}</a></li>')
            html.append('</ul>')
    html.append('</section>')
    return "\n".join(html)

def build_ok_page():
    header = load_header()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    figs, vids, srcs = list_figs(), list_vids(), list_src()
    pairs = pair_two_three(figs, vids)
    parts = [header, '<main class="container">']
    parts.append(section_pairs(pairs))
    parts.a
