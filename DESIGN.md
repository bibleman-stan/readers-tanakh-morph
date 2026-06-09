# readers-tanakh-morph — Design decisions

Browser-based morpheme reader for the Hebrew Bible, sibling of `readers-gnt-morph`
(morph.gnt-reader.com). Target domain: **morph.tanakh-reader.com**.

Ratified by Stan 2026-06-06 ("agree with both your recommendations" + "I will leave it
to your judgment to decide what are the key decision points for encoding/visualizing
hebrew grammar").

## The decisions

### 1. Substrate: BHSA morpheme features (gold, not engine-derived)

The Greek sibling needed a 1,110-line decomposition engine (`morpheus.py`) because
MorphGNT gives parse codes, not morpheme boundaries. **BHSA ships morpheme segmentation
natively** — per word-slot, in pointed Hebrew:

| BHSA feature | Morpheme | Example (Gen 37:5) |
|---|---|---|
| `g_pfm_utf8` | preformative (imperfect/wayyiqtol prefix) | יַּ in וַיַּחֲלֹם |
| `g_vbs_utf8` | verbal-stem affix (hif ה, nif נ, hit הת…) | ה in הִקְטִיל |
| `g_lex_utf8` | lexeme core (stem) | חֲלֹם |
| `g_vbe_utf8` | verbal ending (person/gender/number) | תָּ in קָטַלְתָּ |
| `g_nme_utf8` | nominal ending | ִים in אֱלֹהִים |
| `g_prs_utf8` | pronominal suffix | ו in אֶחָיו |
| `g_uvf_utf8` | univalent final (directional he, paragogic) | ָה in אַרְצָה |

Prefix particles (ו, ב, ל, כ, מ, ה-article, ש) are **separate BHSA word-slots** already —
no splitting needed; they render as distinct colored segments within the printed word.

Validation = BHSA-internal consistency checks, NOT trust-the-engine. BHSA is itself
ETCBC-curated gold; our risk surface is extraction/render bugs, not decomposition errors.

### 2. Binyan as first-class visual dimension

BHSA `vs` (verbal stem) drives a binyan badge + color per verb: qal / nif / piel / pual /
hif / hof / hitp (+ rare: poel, polel, etc. — bucket as "minor stems" with explicit label).
This is THE core Hebrew-verb recognition skill; Greek had no analog. Toggleable layer.

### 3. Root (shoresh) prominence

Tap/click a word → lexeme card shows: consonantal root (from BHSA `lex`, stripped of
disambiguation marks), gloss, binyan + tense for verbs, full BHSA morphology. Weak-verb
camouflage (assimilated-nun hifil יַּגֵּד ← נגד, hollow, III-he) is exactly what the
morpheme-segment display makes visible: the learner sees the missing radical as a gap
between preformative and truncated core.

### 4. Niqqud ON by default; te'amim OFF by default (display toggle)

Display-layer choice only — the source text (BHSA `g_word_utf8`) is never mutated.
Te'amim stripping happens at render time via Unicode-range filter (U+0591–U+05AF accents,
keeping U+05B0–U+05BC+ points). Learners need pointing; cantillation is opt-in.

### 5. Sense-lines from readers-tanakh v2/heb (live ATU layer)

`SENSE_LINES_DIR = C:/Users/bibleman/repos/readers-tanakh/data/text-files/v2/heb`
(env-overridable), consumed read-only, SHA-256 manifest sync (`sync_senselines.py`,
ported from the Greek sibling — pointed at the LIVE layer from day one; the Greek repo's
dead-v4-path defect is the cautionary tale). Naming: `NN-<book>/<book>-NN.txt`,
verse-ref line then Hebrew lines (same shape as Greek).

### 6. Aramaic portions included, labeled

Dan 2:4b–7:28, Ezra 4:8–6:18, 7:12–26 (BHSA `language` feature at word level). Same
morpheme features populated; UI shows an "Aramaic" badge on chapters/verses in range.
Binyan names switch to Aramaic stems (peal/pael/haphel…) per BHSA `vs` values.

### 7. Validator FIRST (HANDOFF.md Part 1.5 directive)

`validate_chapter.py` ships before any display polish. Checks:
- **Reassembly**: concatenated morpheme segments == `g_word_utf8` surface (exact, per word)
- **Verse coverage**: every BHSA word-slot in the chapter appears exactly once in output
- **Binyan sanity**: every `sp=verb` has a `vs` ≠ NA; every non-verb has no binyan badge
- **Suffix agreement**: `prs` segment present iff BHSA `prs` non-empty
- **Sense-line coverage**: every word assigned to exactly one sense-line; line text
  (consonants) matches the v2/heb file content
- **Aramaic flagging**: every word with `language=Aramaic` is inside a flagged range
- Report as coverage percentages + specific findings (Greek validator format)

### 8. Glosses: BHSA `gloss` feature (per-lexeme, ETCBC-curated)

Free, instant, consistent. Context-sensitive gloss refinement deferred (the Greek repo's
`inflect_gloss.py` person/number inflection layer can port later if BHSA's bare lexeme
glosses read poorly in practice).

### 9. Staged rollout

Genesis 1 + Ruth (4 chs) pilot → validator green → Stan eyeballs → bulk 39 books
(~929 chapters). Bulk regen target < 5 min (Greek does 260 chapters in ~23 s; Hebrew has
~3.5× the words plus TF load time ~30 s once per run).

## Architecture (mirrors the Greek sibling)

```
BHSA TF (biblical-corpora/bhsa/tf/2021)          readers-tanakh v2/heb sense-lines
        │                                                  │
        └────────► src/generate_chapter.py ◄───────────────┘
                          │  (extraction + line assignment)
                          ▼
                 build/<book>/<ch>.json     ← validate_chapter.py gates here
                          │
                          ▼  src/build_html.py + templates/chapter.html (RTL)
                 docs/<book>/<ch>.html      ← GitHub Pages, CNAME morph.tanakh-reader.com
```

Color-coded toggleable layers (RTL-adapted from Greek template):
**prefix-particles · preformative · stem-affix · core/stem · verbal ending ·
nominal ending · pronominal suffix · univalent final** + binyan badges.

## Division of labor for go-live

Claude: full local build + push-ready repo. Stan: create GitHub repo
`bibleman-stan/readers-tanakh-morph`, then Claude pushes; Stan adds custom domain
morph.tanakh-reader.com in Pages settings + DNS CNAME record at the registrar.
