#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
import re

# ---- 仓库信息（GitHub Actions 会自动从 env 取；本地跑用默认值）----
REPO_FULL = os.getenv("GITHUB_REPOSITORY", "kl543/rydberg-polaritons-relphase")  # user/repo
BRANCH    = os.getenv("GITHUB_REF_NAME", "main")
OWNER, REPO_NAME = (REPO_FULL.split("/", 1) + [""])[:2]

# ---- 路径 ----
ROOT      = Path(__file__).resolve().parents[1]     # repo root
OUT_HTML  = ROOT / "index.html"
ASSETS    = ROOT / "assets"

FIG_DIR   = ROOT / "figures" / "schematics"
VID_DIR   = ROOT / "videos"
SRC_DIR   = ROOT / "src"

MAIN_SITE    = "https://kl543.github.io"
PROJECTS_URL = f"{MAIN_SITE}/projects.html"

# ------------------------ 小工具 ------------------------
def q(p: Path | str) -> str:
    if isinstance(p, Path):
        p = p.as_posix()
    return quote(p, safe="/-._")

def h(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )

# ------------------------ 共享页眉（与 MBE3 同风格） ------------------------
def load_site_header() -> str:
    for p in [ROOT / "_site-header.html", ROOT.parent / "_site-header.html"]:
        if p.exists():
            return p.read_text(encoding="utf-8")
    # fallback header（标题改为本仓库主题）
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
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
.center{{text-align:center}}
.backline{{margin:6px 0 0;}}
.run-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin-top:8px}}
.tile{{display:block;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;text-decoration:none;color:inherit}}
.tile img{{width:100%;display:block;aspect-ratio:4/3;object-fit:cover}}
.tile .cap{{padding:8px 10px;font-size:13px;color:var(--muted);border-top:1px solid var(--line)}}
video.player{{width:100%;height:auto;border:1px solid var(--line);border-radius:12px;background:#000}}
</style>
</head>
<body>
<header>
  <h1>Rydberg Polaritons — Relative-Phase Dynamics</h1>
  <div class="muted">Schematic figures and videos for biphoton/triphoton relative-phase evolution</div>
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

# ------------------------ 资源收集 ------------------------
def ensure_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    # 单独 style.css（如果你将来想共用同一个 _site-header.html 的 style，这里也可留空）
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")  # 防止 Jekyll 处理

def key_from_name(name: str) -> str | None:
    n = name.lower()
    if re.search(r"\bthree\b", n):
        return "three"
    if re.search(r"\btwo\b", n):
        return "two"
    return None

def list_figures() -> list[str]:
    if not FIG_DIR.exists():
        return []
    exts = (".png", ".svg", ".jpg", ".jpeg", ".webp")
    items = [p for p in FIG_DIR.iterdir() if p.suffix.lower() in exts and p.is_file()]
    items.sort(key=lambda p: p.name.lower())
    return [p.relative_to(ROOT).as_posix() for p in items]

def list_videos() -> list[str]:
    if not VID_DIR.exists():
        return []
    items = sorted(VID_DIR.glob("*.mp4"), key=lambda p: p.name.lower())
    return [p.relative_to(ROOT).as_posix() for p in items]

def list_src_files() -> list[str]:
    if not SRC_DIR.exists():
        return []
    items = [p for p in SRC_DIR.iterdir() if p.is_file() and p.suffix.lower() in (".m", ".py")]
    items.sort(key=lambda p: p.name.lower())
    return [p.relative_to(ROOT).as_posix() for p in items]

def pair_first_match(figs: list[str], vids: list[str]) -> list[dict]:
    """按 Two/Three 做一对多里取第一对（有一项缺失也照样显示）。"""
    fig_map, vid_map = {}, {}
    for rel in figs:
        k = key_from_name(Path(rel).name)
        if k and k not in fig_map:
            fig_map[k] = rel
    for rel in vids:
        k = key_from_name(Path(rel).name)
        if k and k not in vid_map:
            vid_map[k] = rel
    items = []
    for k in ("two", "three"):
        if k not in fig_map and k not in vid_map:
            continue
        if k == "two":
            title = "Two Rydberg Polaritons — Relative-Phase Evolution"
            cap   = ("Relative phase Δϕ(t) for two Rydberg polaritons propagating along z "
                     "with velocities v_g1, v_g2; each induces a blockade region of radius R_b.")
        else:
            title = "Three Rydberg Polaritons — Relative-Phase Evolution"
            cap   = ("Pairwise phases Δϕ₁₂, Δϕ₂₃, Δϕ₃₁ (mod 2π) during the propagation of "
                     "three Rydberg polaritons along z with v_g1, v_g2, v_g3; each with blockade radius R_b.")
        items.append({"title": title, "fig": fig_map.get(k, ""), "vid": vid_map.get(k, ""), "cap": cap})
    return items

# ------------------------ 生成各区块 HTML ------------------------
def section_pairs(items: list[dict]) -> str:
    if not items:
        return '<div class="muted">No paired items detected (Two/Three).</div>'
    cards = []
    for it in items:
        title = h(it["title"])
        fig   = f'<div class="thumb"><img src="{q(it["fig"])}" alt="{title} schematic" loading="lazy"></div>' if it["fig"] else ""
        vid   = f'<video class="player" controls preload="metadata" src="{q(it["vid"])}"></video>' if it["vid"] else ""
        cards.append(
            f"""<section class="card">
<h2>{title}</h2>
{fig}
{vid}
<p class="muted">{h(it["cap"])}</p>
</section>"""
        )
    return "\n".join(cards)

def section_figures(figs: list[str]) -> str:
    html = ['<section class="card">', '<h2>Schematics</h2>']
    if not figs:
        html.append('<div class="muted">No figures yet.</div>')
    else:
        html.append('<div class="grid">')
        for rel in figs:
            name = h(Path(rel).name)
            html.append(f'<a class="tile" href="{q(rel)}" target="_blank" rel="noreferrer">'
                        f'<img src="{q(rel)}" alt="{name}" loading="lazy">'
                        f'<div class="cap">{name}</div></a>')
        html.append('</div>')
    html.append('</section>')
    return "\n".join(html)

def section_videos(vids: list[str]) -> str:
    html = ['<section class="card">', '<h2>Videos</h2>']
    if not vids:
        html.append('<div class="muted">No videos yet.</div>')
    else:
        for rel in vids:
            name = h(Path(rel).name)
            html.append('<div style="margin:10px 0 18px">')
            html.append(f'<b>{name}</b><br>')
            html.append(f'<video class="player" controls preload="metadata" src="{q(rel)}"></video>')
            html.append('</div>')
    html.append('</section>')
    return "\n".join(html)

def section_src(srcs: list[str]) -> str:
    html = ['<section class="card">', '<h2>Source Code</h2>']
    if not srcs:
        html.append('<div class="muted">No source files in src/.</div>')
    else:
        html.append('<ul style="margin:6px 0 0 18px">')
        for rel in srcs:
            name = h(Path(rel).name)
            html.append(f'<li><a class="btn" href="{q(rel)}">{name}</a></li>')
        html.append('</ul>')
    html.append('</section>')
    return "\n".join(html)

# ------------------------ 拼装整个页面 ------------------------
def build_html() -> str:
    ensure_assets()
    header = load_site_header()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    figs = list_figures()
    vids = list_videos()
    srcs = list_src_files()
    pairs = pair_first_match(figs, vids)

    parts = [header, '<main class="container">']

    # 1) Paired overview（Two/Three 卡片）
    parts.append('<section class="card"><h2>Overview</h2><div class="muted">Auto-paired by filename keywords (“Two” / “Three”).</div></section>')
    parts.append(section_pairs(pairs))

    # 2) 全部图 & 3) 全部视频 & 4) 源码
    parts.append(section_figures(figs))
    parts.append(section_videos(vids))
    parts.append(section_src(srcs))

    parts.append(f'<div class="center muted" style="margin:24px 0;">Last updated: {now_str} — {OWNER}/{REPO_NAME}@{BRANCH}</div>')
    parts.append('</main></body></html>')
    return "\n".join(parts)

def main():
    OUT_HTML.write_text(build_html(), encoding="utf-8")
    print(f"[relphase] Wrote {OUT_HTML}")

if __name__ == "__main__":
    main()
