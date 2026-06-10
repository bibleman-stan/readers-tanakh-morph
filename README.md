# Tanakh Morpheme Reader

Browser-based morpheme reader for the Hebrew Bible, live at **morph.tanakh-reader.com**.
Every Hebrew word is decomposed into its morphological pieces — prefix particles,
preformative, stem affix, lexical core, verbal/nominal ending, univalent final,
pronominal suffix — each rendered as a color-coded, toggleable layer. Verbs carry
binyan badges (Qal, Nifal, Piel, Pual, Hifil, Hofal, Hitpael + minor and Aramaic
stems). Niqqud displays by default; cantillation (te'amim) is an opt-in toggle.

Sibling project of the [Greek NT morpheme reader](https://morph.gnt-reader.com)
(`readers-gnt-morph`) and the [Tanakh Reader](https://tanakh-reader.com)
(`readers-tanakh`), whose sense-line layout this reader follows.

## How it works

The morpheme segmentation is **BHSA-native**: the ETCBC's
[BHSA](https://github.com/ETCBC/bhsa) corpus ships per-word morpheme features
(`g_pfm`, `g_vbs`, `g_lex`, `g_vbe`, `g_nme`, `g_prs`, `g_uvf`) in pointed Hebrew.
This project's engine re-attaches cantillation to those boundaries (accents and
meteg ride the segment they fall inside) and renders single-file HTML pages.

```
BHSA Text-Fabric  ──►  src/generate_chapter.py  ──►  build/<book>/<ch>.json
readers-tanakh sense-lines ──┘                              │
                                                            ▼
                              src/validate_chapter.py (7-check gate)
                                                            │
                                                            ▼
                              src/build_html.py  ──►  docs/<book>/<ch>.html
```

- **Build everything**: `PYTHONIOENCODING=utf-8 python src/bulk_generate.py`
  (validator-gated; ~1-2 min after the one-time TF load)
- **One chapter**: `python src/generate_chapter.py --book ruth --chapter 1`
  then `python src/build_html.py --book ruth --chapter 1`
- **Validate**: `python src/validate_chapter.py --book ruth`

## Validation

Seven mechanical checks per chapter against BHSA ground truth: segment
reassembly (concatenated morphemes must equal the surface form exactly),
word coverage and order, binyan presence, pronominal-suffix presence,
sense-line agreement (with ketiv/qere tolerance), Aramaic flagging, and a
decomposition-coverage metric. The whole corpus must pass before HTML ships.

## Data sources

See [NOTICE.md](NOTICE.md) for attribution. Primary substrate: BHSA (ETCBC,
CC BY-NC 4.0). Sense-line layout: the Tanakh Reader's ATU (atomic thought
unit) line breaks.

## License

Code: MIT (see LICENSE). Data: per the upstream licenses in NOTICE.md.
