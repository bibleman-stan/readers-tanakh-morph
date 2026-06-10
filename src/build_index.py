#!/usr/bin/env python3
"""Generate docs/index.html — the landing page with the 39-book grid."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from books import BOOKS

_REPO_ROOT = os.path.dirname(_HERE)

SECTIONS = [
    ('Torah', ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy']),
    ('Former Prophets', ['joshua', 'judges', '1samuel', '2samuel', '1kings', '2kings']),
    ('Latter Prophets', ['isaiah', 'jeremiah', 'ezekiel', 'hosea', 'joel', 'amos',
                         'obadiah', 'jonah', 'micah', 'nahum', 'habakkuk',
                         'zephaniah', 'haggai', 'zechariah', 'malachi']),
    ('Writings', ['psalms', 'job', 'proverbs', 'ruth', 'songofsongs',
                  'ecclesiastes', 'lamentations', 'esther', 'daniel', 'ezra',
                  'nehemiah', '1chronicles', '2chronicles']),
]

PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tanakh Morpheme Reader</title>
<meta name="description" content="Morpheme-by-morpheme Hebrew Bible reader — every word color-coded by prefix, preformative, stem, ending, and suffix, with binyan badges.">
<meta property="og:title" content="Tanakh Morpheme Reader">
<meta property="og:description" content="Morpheme-by-morpheme Hebrew Bible reader with color-coded morphology layers and binyan badges.">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<style>
:root {{
  --bg:#1b1d22; --fg:#e8e6e0; --dim:#9a978f; --card:#26282f;
  --accent:#d9a548; --link:#8db4e2;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg);
       font:16px/1.6 Georgia, 'Times New Roman', serif; }}
.wrap {{ max-width:880px; margin:0 auto; padding:32px 20px 64px; }}
h1 {{ font-size:1.9em; margin:0 0 4px; color:var(--accent); }}
.sub {{ color:var(--dim); margin:0 0 28px; }}
.heb {{ font-family:'SBL Hebrew','Ezra SIL','Taamey Frank CLM','David Libre',serif;
        font-size:1.35em; direction:rtl; }}
h2 {{ font-size:1.1em; color:var(--dim); text-transform:uppercase;
     letter-spacing:.08em; margin:30px 0 10px; border-bottom:1px solid #34363e;
     padding-bottom:4px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
        gap:8px; }}
.bk {{ display:block; background:var(--card); border-radius:8px; padding:10px 12px;
      text-decoration:none; color:var(--fg); border:1px solid #34363e; }}
.bk:hover {{ border-color:var(--accent); }}
.bk .n {{ font-weight:bold; }}
.bk .c {{ color:var(--dim); font-size:.85em; }}
.note {{ background:var(--card); border-radius:8px; padding:14px 16px;
        margin:24px 0; color:var(--dim); font-size:.95em; }}
.note b {{ color:var(--fg); }}
a {{ color:var(--link); }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Tanakh Morpheme Reader</h1>
  <p class="sub">Every word of the Hebrew Bible, decomposed.
     <span class="heb">בְּ·רֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים</span></p>

  <div class="note">
    Each Hebrew word is split into its morphological pieces — prefix particles,
    preformative, stem, verbal/nominal endings, pronominal suffixes — rendered as
    color-coded layers you can toggle. Verbs carry <b>binyan</b> badges
    (Qal, Nifal, Piel, Pual, Hifil, Hofal, Hitpael). Niqqud shows by default;
    cantillation (te&rsquo;amim) is a toggle. Tap any word for its full
    morphology and gloss. Line layout follows the
    <a href="https://tanakh-reader.com">Tanakh Reader</a>&rsquo;s sense lines;
    morphology is sourced from the
    <a href="https://github.com/ETCBC/bhsa">BHSA</a> (ETCBC).
    Greek sibling: <a href="https://morph.gnt-reader.com">morph.gnt-reader.com</a>.
  </div>

{sections}
</div>
</body>
</html>
'''


def main():
    parts = []
    for title, codes in SECTIONS:
        parts.append(f'  <h2>{title}</h2>\n  <div class="grid">')
        for code in codes:
            meta = BOOKS[code]
            parts.append(
                f'    <a class="bk" href="{code}/1.html">'
                f'<span class="n">{meta["display"]}</span><br>'
                f'<span class="c">{meta["chapters"]} chapter{"s" if meta["chapters"] > 1 else ""}</span></a>')
        parts.append('  </div>')
    html = PAGE.format(sections='\n'.join(parts))
    out = os.path.join(_REPO_ROOT, 'docs', 'index.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'wrote {out} ({os.path.getsize(out):,} bytes)')


if __name__ == '__main__':
    main()
