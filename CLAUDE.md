# readers-tanakh-morph — Claude Code Instructions (thin stub)

This repo is operated by the **unified user-home orchestrator-Claude** at `C:\Users\bibleman\`. Stan opens VSCode at user-home, not at this repo.

If you are a Claude that spawned in this workspace (VSCode opened at this repo): **hand off**. Tell Stan to switch to a vault-Claude window at `C:\Users\bibleman\`. The unified Claude has full cross-repo context; per-repo Claudes don't.

## What this project is (for collaborators / forks)

Browser-based morpheme reader for the Hebrew Bible. Each Hebrew word decomposed into morphological pieces (prefix particles → preformative → stem affix → core → verbal/nominal ending → univalent final → pronominal suffix) with color-coded toggleable layers, binyan badges, and niqqud/te'amim display toggles. Target domain **morph.tanakh-reader.com** (GitHub Pages from `docs/`).

Unlike the Greek sibling (`readers-gnt-morph`, which needed a hand-built decomposition engine), the morpheme segmentation here is **BHSA-native** — the ETCBC's `g_pfm/g_vbs/g_lex/g_vbe/g_nme/g_prs/g_uvf` features ARE the decomposition; this repo's engine re-attaches cantillation to those boundaries and renders.

- **Sibling to**: `readers-tanakh` (consumes its v2/heb sense-lines; never writes to it) and `readers-gnt-morph` (architecture template)
- **Substrate**: BHSA 2021 Text-Fabric at `~/repos/biblical-corpora/bhsa/tf/2021` (env `BHSA_TF_DIR`)
- **Sense-lines**: `~/repos/readers-tanakh/data/text-files/v2/heb/` (env `SENSE_LINES_DIR`) — the LIVE v1.5 binding-rule layer. If readers-tanakh ever moves its live dir, update BOTH constants (generate_chapter.py, sync_senselines.py) — the Greek sibling shipped stale line-breaks for 2 weeks on a dead path (fixed 2026-06-06).
- **Build**: `src/bulk_generate.py` (whole Tanakh, validator-gated); `src/generate_chapter.py --book X --chapter N` + `src/build_html.py --book X --chapter N` per chapter
- **Validation**: `src/validate_chapter.py` — 7 checks vs BHSA ground truth (reassembly, coverage, binyan, suffix, sense-lines w/ ketiv-qere tolerance, Aramaic flags, seg-mismatch). Run BEFORE display work, always.
- **Design record**: `DESIGN.md` — the 9 ratified decisions (2026-06-06)

## Known data caveats

- Sense files are TAHOT-form; BHSA differs on ketiv/qere (~3.5% of verses corpus-wide). The line-aligner maps through difflib opcodes; the C5 validator check tolerates ratio ≥ 0.85 per line. See the BHSA-canon-migration arc in the orchestrator memory.
- BHSA compound proper names (בית לחם) are ONE word-slot with an internal space.
- Aramaic ranges (Dan 2:4–7:28, Ezra 4:8–6:18, 7:12–26) flagged per-word via BHSA `language`; stems display Aramaic binyan names (peal/pael/hafel...).

## Methodology canon (cross-corpus)

`~/repos/atu-method/docs/`.
