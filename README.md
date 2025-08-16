# Rydberg Polaritons: Time-Evolution & Relative-Phase Dynamics (MATLAB)

MATLAB scripts for simulating and visualizing the relative-phase evolution of two and three Rydberg polaritons in quasi-1D and 2D media under Rydberg blockade. The repository also includes two schematic figures and two short MP4 clips.

## Layout
- `src/` — MATLAB `.m` scripts (1D/2D; two/three polaritons).
- `figures/schematics/` — schematic PNGs.
- `videos/` — MP4 clips.
- `scripts/gen_docs.py` — generates `index.html` for GitHub Pages.

## Requirements
- MATLAB R2021b or newer.

## Quick start
1. Add the source directory and run a script:
   ```matlab
   addpath('src');
   oned_twop_allm_v4;    % 1D, two polaritons (example)
