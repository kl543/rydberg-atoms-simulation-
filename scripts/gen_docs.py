#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

REPO_FULL = os.getenv("GITHUB_REPOSITORY", "kl543/rydberg-atoms-simulation-")
BRANCH    = os.getenv("GITHUB_REF_NAME", "main")
OWNER, REPO_NAME = (REPO_FULL.split("/", 1) + [""])[:2]

ROOT     = Path(__file__).resolve().parents[1]
OUT_HTML = ROOT / "index.html"
ASSETS   = ROOT / "assets"

FIG_DIR = ROOT / "figures" / "schematics"
VID_DIR = ROOT / "videos"
SRC_DIR = ROOT / "src"

MAIN_SITE    = "https://kl543.github.io"
PROJECTS_URL = f"{MAIN_SITE}/projects.html"

def q(p: Path | str) -> str:
    if isinstance(p, Path): p = p.as_posix()
    return quote(p, safe="/-._")

def h(s: str) -> str:
    return (s.replace("&","&amp;").replace("<","&lt;")
              .replace(">","&gt;").replace('"',"&quot;"))

def load_site_header() -> str:
    for p in [ROOT / "_site-header.html", ROOT.parent / "_site-header.html"]:
        if p.exists(): return p.read_text(encoding="utf-8")
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Rydberg Polaritons — Relative-Phase Dynamics — Kaiming Liu</title>
<style>
:root{{--line:#e9e9e9;--muted:#666;--ink:#111}}
body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);line-height:1.6}}
header{{background:#111;color:#fff;padding:30px 16px;text-align:center}}
nav{{display:flex;gap:14px;justify-content:center;margin:10px 0 0}}
nav a{{color:#fff;text-decoration:none;opacity:.9}} nav a:hover{{opacity:1}}
.container{{max-width:1040px;margin:24px auto;padding:0 16px}}
.muted{{color:var(--muted)}}
.card{{border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:16px 0;background:#fff}}
h1,h2,h3{{margin:.2rem 0 .6rem}}
.btn{{display:inline-block;border:1px solid var(--line);padding:8px 12px;border-radius:10px;text-decoration:none;margin-right:8px;color:#111}}
.btn:hover{{background:#f6f6f6}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
.thumb{{border:1px solid var(--line);border-radius:12px;padding:6px;background:#fff}}
.thumb img{{width:100%;height:auto;display:block;border-radius:8px}}
video.player{{width:100%;height:auto;border:1px solid var(--line);border-radius:12px;background:#000}}
.center{{text-align:center}}
.backline{{margin:6px 0 0;}}
</style>
</head><body>
<header>
  <h1>Rydberg Polaritons — Relative-Phase Dynamics</h1>
  <div class="muted">Schematic figures and MP4 clips (Two/Three)</div>
  <div class="backline"><a href="{PROJECTS_URL}" style="color:#fff;text-decoration:underline;">Back to Projects</a></div>
  <nav>
    <a href="{MAIN_SITE}/index.html">About</a>
    <a href="{MAIN_SITE}/interests.html">Interests</a>
    <a href="{MAIN_SITE}/projects.html"><b>Projects</b></a>
    <a href="{MAIN_SITE}/coursework.html">Coursework</a>
    <a href="{MAIN_SITE}/contact.html">Contact</a>
  </nav>
</header>
"""

def ensure_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    # 独立样式文件（即使页眉内含样式，也生成一个，避免引用 404）
    (ASSETS / "style.css").write_text("/* placeholder */\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")

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
    return [p.relative_to(ROOT).as_posix() for p in items]

def list_vids() -> list[str]:
    if not VID_DIR.exists(): return []
    items = sorted(VID_DIR.glob("*.mp4"), key=lambda p: p.name.lower())
    return [p.relative_to(ROOT).as_posix() for p in items]

def list_src() -> list[str]:
    if not SRC_DIR.exists(): return []
    items = [p for p in SRC_DIR.iterdir() if p.is_file() and p.suffix.lower() in {".m",".py"}]
    items.sort(key=lambda p: p.name.lower())
    return [p.relative_to(ROOT).as_posix() for p in items]

def pair_two_three(figs: list[str], vids: list[str]) -> list[dict]:
    f, v = {}, {}
    for rel in figs:
        k = key_from_name(Path(rel).name)
        if k and k not in f: f[k] = rel
    for rel in vids:
        k = key_from_name(Path(rel).name)
        if k and k not in v: v[k] = rel
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

def section_pairs(items: list[dict]) -> str:
    if not items:
        return '<section class="card"><h2>Overview</h2><div class="muted">No items detected (Two/Three).</div></section>'
    cards = ['<section class="card"><h2>Overview</h2>']
    for it in items:
        title = h(it["title"])
        fig = f'<div class="thumb"><img src="{q(it["fig"])}" alt="{title} schematic" loading="lazy"></div>' if it["fig"] else ""
        vid = f'<video class="player" controls preload="metadata" src="{q(it["vid"])}"></video>' i
