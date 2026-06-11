#!/usr/bin/env python3
"""
Generate morpheme-decomposed JSON for a Tanakh chapter from BHSA.

Unlike the Greek sibling (which needed a 1,110-line decomposition engine),
BHSA ships morpheme segmentation natively: g_pfm / g_vbs / g_lex / g_vbe /
g_nme / g_prs / g_uvf (_utf8 variants, pointed Hebrew). This module reads
those features, assembles ordered morpheme segments per word, attaches
binyan/tense/gloss metadata, and assigns words to sense-lines from the
sibling readers-tanakh repo's live v2/heb layer.

Morpheme order within a Hebrew word (surface order, right-to-left in
display but logical order here):
    pfm (preformative) -> vbs (stem affix) -> lex (core) -> vbe (verbal
    ending) -> nme (nominal ending) -> uvf (univalent final) -> prs
    (pronominal suffix)
Prefix particles (waw, prepositions, article) are separate BHSA word-slots
and arrive as their own single-segment words; the renderer joins slots
that share a printed word (BHSA `trailer` empty = no space follows).

Usage:
  PYTHONIOENCODING=utf-8 python src/generate_chapter.py --book genesis --chapter 1
  PYTHONIOENCODING=utf-8 python src/generate_chapter.py --book ruth          # all chapters
"""
import argparse
import json
import os
import re
import sys
import unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from books import BOOKS, BINYANIM, TENSES

_REPO_ROOT = os.path.dirname(_HERE)
BUILD_DIR = os.path.join(_REPO_ROOT, 'build')

BHSA_TF = os.environ.get(
    'BHSA_TF_DIR',
    'C:/Users/bibleman/repos/biblical-corpora/bhsa/tf/2021',
)
# Sense-line files live in the sibling readers-tanakh repo. The LIVE layer
# is v2/heb (the v1.5 binding-rule stage output; dir name is historical).
# Pointed at the live layer from day one — the Greek sibling's dead-v4-path
# defect (fixed 2026-06-06) is the cautionary tale.
SENSE_LINES_DIR = os.environ.get(
    'SENSE_LINES_DIR',
    'C:/Users/bibleman/repos/readers-tanakh/data/text-files/v2/heb',
)
# Transliteration (modern-Israeli style, TAHOT-derived) — the SAME layer
# tanakh-reader.com displays, consumed read-only for cross-site consistency.
# One ` | `-separated unit per printed Hebrew word; maqaf-joined words are
# separate units. Lives beside the sense-lines in readers-tanakh.
TRANSLIT_DIR = os.environ.get(
    'TRANSLIT_DIR',
    'C:/Users/bibleman/repos/readers-tanakh/data/text-files/v2/translit',
)

# Morpheme slots in BHSA surface order, with the (feature, css-class) pairs.
# css classes: pfx is reserved for prefix-particle word-slots (handled at
# word level, not via these features).
MORPH_SLOTS = [
    ('g_pfm_utf8', 'pfm'),   # preformative
    ('g_vbs_utf8', 'vbs'),   # verbal-stem affix
    ('g_lex_utf8', 'stm'),   # lexeme core
    ('g_vbe_utf8', 'vbe'),   # verbal ending
    ('g_nme_utf8', 'nme'),   # nominal ending
    ('g_uvf_utf8', 'uvf'),   # univalent final
    ('g_prs_utf8', 'prs'),   # pronominal suffix
]

# Parts of speech that render as prefix-particle segments when they are
# their own word-slot glued (no trailer) to the following slot.
PREFIX_POS = {'prep', 'art', 'conj'}

_api = None


def tf_api():
    """Load BHSA Text-Fabric once per process."""
    global _api
    if _api is None:
        from tf.fabric import Fabric
        features = (
            'otype book chapter verse '
            'g_word_utf8 trailer_utf8 '
            'g_pfm_utf8 g_vbs_utf8 g_lex_utf8 g_vbe_utf8 '
            'g_nme_utf8 g_prs_utf8 g_uvf_utf8 '
            'vs vt sp ps gn nu st lex language gloss '
        )
        TF = Fabric(locations=BHSA_TF, silent=True)
        _api = TF.load(features, silent=True)
        if _api is False:
            raise RuntimeError(f'BHSA TF load failed from {BHSA_TF}')
    return _api


def strip_accents(s):
    """Remove te'amim (cantillation, U+0591-U+05AF) but keep niqqud.

    Used for sense-line matching only — the JSON stores the fully pointed
    form and the display layer does its own runtime filtering.
    """
    return ''.join(c for c in s if not (0x0591 <= ord(c) <= 0x05AF))


def consonants_only(s):
    """Strip all Hebrew points + accents + punctuation, keep consonants + maqaf.

    Punctuation stripped: paseq (U+05C0), sof pasuq (U+05C3), nun hafukha
    (U+05C6) — standalone marks that are not word content.
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if not unicodedata.combining(c) and ord(c) not in (0x05C0, 0x05C3, 0x05C6)
    )


# BHSA morpheme features prefix a U+059C (geresh muqdam) as a
# morpheme-boundary placeholder; it is a marker, never content.
_BHSA_MARKER = '֜'


def _is_accent(c):
    # Cantillation (U+0591-05AF) plus meteg (U+05BD), which the BHSA
    # morpheme features omit but the surface form carries.
    return 0x0591 <= ord(c) <= 0x05AF or ord(c) == 0x05BD


# Final <-> medial Hebrew letter equivalence: BHSA morpheme features use the
# lexeme's citation form (e.g. final fe in רַחֶף) where the surface uses the
# positional form (medial pe in מְרַחֶפֶת). Matching treats the pairs as
# equal; the emitted segment always carries the SURFACE character.
_FINAL_MEDIAL = {
    'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ',
    'כ': 'ך', 'מ': 'ם', 'נ': 'ן', 'פ': 'ף', 'צ': 'ץ',
}


def _ch_eq(a, b):
    return a == b or _FINAL_MEDIAL.get(a) == b


def segment_surface(surface, morphemes):
    """Split the accented surface into segments matching the (accent-free)
    BHSA morpheme features.

    morphemes: list of (text, css) where text is the feature value with
    the U+059C marker stripped. Returns list of {'t','m'} whose
    concatenation equals surface exactly (accents ride with the segment
    they fall inside), or None when alignment fails.
    """
    segs = []
    si = 0  # index into surface
    n = len(surface)
    for mtext, css in morphemes:
        target = [c for c in mtext if not _is_accent(c)]
        if not target:
            continue  # null morpheme (marker-only slot)
        ti = 0
        start = si
        while si < n and ti < len(target):
            if _ch_eq(surface[si], target[ti]):
                ti += 1
                si += 1
            elif _is_accent(surface[si]):
                si += 1  # accent rides with current segment
            else:
                return None  # real mismatch
        if ti < len(target):
            return None
        # trailing accents attach to this segment (unless more morphemes
        # follow and the next char starts the next morpheme's first char)
        while si < n and _is_accent(surface[si]):
            si += 1
        segs.append({'t': surface[start:si], 'm': css})
    if si != n:
        # leftover surface (e.g. furtive patach handling) — attach to last seg
        if segs and all(_is_accent(c) or unicodedata.combining(c) for c in surface[si:]):
            segs[-1]['t'] += surface[si:]
        else:
            return None
    return segs


def word_record(api, w):
    """Build the JSON record for one BHSA word-slot."""
    F, L = api.F, api.L
    surface = F.g_word_utf8.v(w) or ''
    rec = {'txt': surface}

    # Collect non-null morphemes (marker stripped)
    morphemes = []
    for feat, css in MORPH_SLOTS:
        val = getattr(F, feat).v(w)
        if not val:
            continue
        val = val.replace(_BHSA_MARKER, '')
        if not val:
            continue  # marker-only slot (null morpheme)
        morphemes.append((val, css))

    segs = segment_surface(surface, morphemes) if morphemes else None
    if segs:
        rec['segs'] = segs
    else:
        rec['segs'] = [{'t': surface, 'm': 'whole'}]
        if len(morphemes) > 1:
            rec['seg_mismatch'] = True  # validator surfaces these

    sp = F.sp.v(w)
    rec['sp'] = sp

    lex_node = L.u(w, otype='lex')
    if lex_node:
        rec['lem'] = F.lex.v(w) or ''
        gl = F.gloss.v(lex_node[0])
        if gl:
            rec['gl'] = gl

    vs = F.vs.v(w)
    if vs and vs != 'NA':
        b = BINYANIM.get(vs, {'display': vs, 'color': 'minor'})
        rec['vs'] = vs
        rec['vsd'] = b['display']
        rec['vsc'] = b['color']
    vt = F.vt.v(w)
    if vt and vt != 'NA':
        rec['vt'] = vt
        rec['vtd'] = TENSES.get(vt, vt)

    for feat in ('ps', 'gn', 'nu', 'st'):
        val = getattr(F, feat).v(w)
        if val and val not in ('NA', 'unknown'):
            rec[feat] = val

    if F.language.v(w) == 'Aramaic':
        rec['arc'] = True

    trailer = F.trailer_utf8.v(w) or ''
    # glued = this slot is printed joined to the next (prefix particles)
    if trailer == '':
        rec['glue'] = True
    elif '־' in trailer:   # maqaf
        rec['maqaf'] = True

    return rec


def load_sense_lines(book_code, chapter):
    """Load sense-line split points for a chapter from readers-tanakh.

    Returns a list of lines, each a list of consonantal word tokens, or
    None when the chapter file is absent.
    File shape:  verse-ref line (e.g. '1:1'), then 1+ Hebrew lines, blank
    line between verses.
    """
    entry = BOOKS.get(book_code)
    if not entry:
        return None
    sc = entry['sense_code']
    if not os.path.isdir(SENSE_LINES_DIR):
        return None
    dir_name = None
    for d in os.listdir(SENSE_LINES_DIR):
        parts = d.split('-', 1)
        if len(parts) == 2 and parts[1] == sc:
            dir_name = d
            break
    if not dir_name:
        return None
    path = os.path.join(SENSE_LINES_DIR, dir_name, f'{sc}-{chapter:02d}.txt')
    if not os.path.exists(path):
        return None

    verses = {}   # verse_num -> list of lines, each a list of consonant tokens
    cur_verse = None
    with open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            m = re.match(r'^(\d+):(\d+)$', line)
            if m:
                cur_verse = int(m.group(2))
                verses[cur_verse] = []
                continue
            if cur_verse is None:
                continue
            # Drop tokens carrying no Hebrew letter (standalone paseq,
            # sof pasuq, etc.) — they are not word-slots and would shift
            # the greedy aligner.
            tokens = [
                consonants_only(t) for t in line.split()
                if any(0x05D0 <= ord(c) <= 0x05EA for c in t)
            ]
            verses[cur_verse].append(tokens)
    return verses


def _matchform(s):
    """Normalize a consonantal string for alignment: drop maqaf, sof pasuq,
    paseq, and ALL whitespace (BHSA compound-name slots carry internal
    spaces; sense-file tokens never do)."""
    return ''.join(c for c in s if c not in '־׃׀' and not c.isspace())


def load_translit(book_code, chapter):
    """Load per-verse transliteration units for a chapter.

    Returns {verse_num: [unit, ...]} with units flattened across the
    file's sense-lines (alignment to Hebrew is by unit COUNT per verse,
    one unit per printed word / maqaf segment), or None when absent.
    """
    entry = BOOKS.get(book_code)
    if not entry or not os.path.isdir(TRANSLIT_DIR):
        return None
    sc = entry['sense_code']
    dir_name = None
    for d in os.listdir(TRANSLIT_DIR):
        parts = d.split('-', 1)
        if len(parts) == 2 and parts[1] == sc:
            dir_name = d
            break
    if not dir_name:
        return None
    path = os.path.join(TRANSLIT_DIR, dir_name, f'{sc}-{chapter:02d}.txt')
    if not os.path.exists(path):
        return None
    verses = {}
    cur = None
    with open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            m = re.match(r'^(\d+):(\d+)$', line)
            if m:
                cur = int(m.group(2))
                verses[cur] = []
                continue
            if cur is None:
                continue
            verses[cur].extend(u.strip() for u in line.split('|') if u.strip())
    return verses


# Hebrew consonant -> plausible translit realizations (modern-Israeli style,
# matching readers-tanakh's clean_translit output). Order longest-first per
# letter; '' = silent (alef/ayin/final he, mater yod/vav).
_TRANSLIT_CONS = {
    'א': ("'", ''), 'ב': ('v', 'b'), 'ג': ('g',), 'ד': ('d',),
    'ה': ('h', ''), 'ו': ('v', 'w', 'u', 'o', ''), 'ז': ('z',),
    'ח': ('ch', 'kh', 'h'), 'ט': ('t',), 'י': ('y', 'i', ''),
    'כ': ('kh', 'ch', 'k'), 'ך': ('kh', 'ch', 'k'), 'ל': ('l',),
    'מ': ('m',), 'ם': ('m',), 'נ': ('n',), 'ן': ('n',), 'ס': ('s',),
    'ע': ("'", ''), 'פ': ('f', 'p'), 'ף': ('f', 'p'),
    'צ': ('tz', 'ts'), 'ץ': ('tz', 'ts'), 'ק': ('k',), 'ר': ('r',),
    'ש': ('sh', 's'), 'ת': ('t',),
}
_TR_VOWELS = set("aeiou")


def split_translit(unit_segs, tr):
    """Split one translit word-string at Hebrew morpheme boundaries.

    unit_segs: flattened [(css_class, consonant_string), ...] across the
    visual unit's records (prefix-particle records pre-classed 'pfx').
    Returns [{'t': piece, 'm': cls}, ...] whose concatenation == tr
    exactly, or None when the consonant-skeleton walk fails to verify.
    Vowels/apostrophes attach to the segment of the consonant they follow.
    Doubling (dagesh forte across a boundary, e.g. vai+yomer) is handled
    by letting a consonant consume a doubled realization.
    """
    tr_l = tr.lower()
    cons_seq = []           # (seg_index, consonant)
    for si, (_cls, cons) in enumerate(unit_segs):
        for c in cons:
            if c in _TRANSLIT_CONS:
                cons_seq.append((si, c))

    n = len(tr_l)

    # DP over (consonant index, translit position) -> parent for backtrack
    from functools import lru_cache
    sys.setrecursionlimit(10000)
    memo = {}

    def walk(ci, pos):
        """Return list of (ci, start, end) matches or None."""
        key = (ci, pos)
        if key in memo:
            return memo[key]
        # consume leading vowels/apostrophes — they attach to PREVIOUS seg
        if ci == len(cons_seq):
            rest = tr_l[pos:]
            result = [] if all(ch in _TR_VOWELS or ch == "'" or ch == '-' for ch in rest) else None
            memo[key] = result
            return result
        # vowels before this consonant belong to the previous consonant's seg
        p = pos
        while p < n and (tr_l[p] in _TR_VOWELS or tr_l[p] == '-'):
            p += 1
        _si, c = cons_seq[ci]
        for var in _TRANSLIT_CONS[c]:
            # doubled realization (dagesh forte): e.g. 'yy', 'mm'
            for cand in ((var + var) if var else None, var):
                if cand is None:
                    continue
                end = p + len(cand)
                if cand == '' or tr_l[p:end] == cand:
                    rest = walk(ci + 1, end if cand else p)
                    if rest is not None:
                        # Silent match (mater lectionis): the vowel run we
                        # skipped REALIZES this consonant (ים = 'im'), so
                        # anchor it at the pre-vowel position.
                        anchor = pos if cand == '' else p
                        result = [(ci, anchor, end if cand else anchor)] + rest
                        memo[key] = result
                        return result
        # silent-consonant fallback at current pos without consuming vowels
        memo[key] = None
        return None

    matches = walk(0, 0)
    if matches is None:
        return None

    # Boundary positions: a new segment begins at the first consumed char of
    # its first consonant (vowels between belong to the previous segment).
    seg_start = {}   # seg_index -> earliest translit pos
    for (ci, start, _end) in matches:
        si = cons_seq[ci][0]
        if si not in seg_start:
            seg_start[si] = start
    # Segments with no consonants (pure-vowel morphemes) inherit boundaries
    cut_points = []
    prev = 0
    pieces = []
    seg_indices = sorted(seg_start)
    for k, si in enumerate(seg_indices):
        start = seg_start[si] if k > 0 else 0
        if k > 0:
            cut_points.append(start)
    cuts = [0] + cut_points + [n]
    # Build pieces per contributing segment, in order
    out = []
    for k, si in enumerate(seg_indices):
        piece = tr[cuts[k]:cuts[k + 1]]
        if not piece:
            continue
        out.append({'t': piece, 'm': unit_segs[si][0]})
    if ''.join(p['t'] for p in out) != tr:
        return None
    if len(out) < 2:
        return None   # nothing to colour — plain tr suffices
    return out


def attach_translit(recs, translit_units):
    """Attach a `tr` field to the head record of each visual word unit.

    A visual unit = a run of glue:true records plus the terminating
    record (mirrors the template's buildUnits). Maqaf-terminated records
    end their unit (translit files give maqaf segments their own unit).
    Attaches ONLY when unit count matches exactly — a count mismatch
    (ketiv/qere divergence verses, compound-name slots) skips the verse
    so misaligned translit can never ship. Returns True if attached.
    """
    units = []   # list of head-record indices
    run_start = None
    for i, (rec, _cons) in enumerate(recs):
        if run_start is None:
            run_start = i
        if not rec.get('glue'):
            units.append(i)   # head = terminating record of the run
            run_start = None
    if run_start is not None:
        units.append(len(recs) - 1)
    if len(units) != len(translit_units):
        return False
    run_start = 0
    for head_idx, tr in zip(units, translit_units):
        recs[head_idx][0]['tr'] = tr
        # Morpheme-coloured split: flatten this unit's segs (prefix-particle
        # records class as pfx at word level, mirroring the renderer).
        unit_segs = []
        for j in range(run_start, head_idx + 1):
            rec = recs[j][0]
            is_pfx = rec.get('glue') and rec.get('sp') in ('prep', 'art', 'conj')
            for seg in rec.get('segs', []):
                cls = 'pfx' if is_pfx else seg.get('m', 'whole')
                unit_segs.append((cls, consonants_only(seg['t'])))
        trs = split_translit(unit_segs, tr)
        if trs:
            recs[head_idx][0]['trs'] = trs
        run_start = head_idx + 1
    return True


def assign_lines(verse_words, sense_lines):
    """Assign each word record (+ its surface consonants) to a sense-line.

    verse_words: list of (rec, consonants) in BHSA order.
    sense_lines: list of lines, each a list of consonantal tokens
                 (tokens may be maqaf-joined groups matching 1+ BHSA slots).
    Returns: list of line-break indices — positions i where a new line
             starts before verse_words[i]. Robust to glued prefix slots:
             we walk the sense tokens and consume BHSA slots greedily by
             consonant matching.
    """
    if not sense_lines:
        return []
    import difflib

    # Build the BHSA-side consonant stream with word-start offsets
    bhsa_str = ''
    word_starts = []   # char offset where word i begins in bhsa_str
    for rec, cons in verse_words:
        word_starts.append(len(bhsa_str))
        bhsa_str += _matchform(cons)

    # Build the sense-side stream and the char offsets where lines 2..N start
    sense_str = ''
    line_offsets = []  # char offset in sense_str where each line li>0 starts
    for li, line in enumerate(sense_lines):
        if li > 0:
            line_offsets.append(len(sense_str))
        sense_str += ''.join(_matchform(t) for t in line)

    if bhsa_str == sense_str:
        # Fast path — direct offset lookup
        mapped = line_offsets
    else:
        # Forms differ (ketiv/qere, TAHOT-vs-BHSA orthography). Map each
        # sense offset through difflib opcodes to the BHSA stream; small
        # local insertions/deletions shift offsets correctly instead of
        # desyncing the rest of the verse.
        sm = difflib.SequenceMatcher(None, sense_str, bhsa_str, autojunk=False)
        opcodes = sm.get_opcodes()

        def map_offset(off):
            for tag, i1, i2, j1, j2 in opcodes:
                if i1 <= off < i2 or (off == i2 and i2 == len(sense_str)):
                    if tag == 'equal':
                        return j1 + (off - i1)
                    return j1  # inside a replace/delete: snap to block start
            return len(bhsa_str)

        mapped = [map_offset(off) for off in line_offsets]

    # Snap each mapped char offset to the nearest word-start boundary
    breaks = []
    for off in mapped:
        best = min(range(len(word_starts)),
                   key=lambda i: abs(word_starts[i] - off))
        if not breaks or best > breaks[-1]:
            breaks.append(best)
    return [b for b in breaks if b > 0]


def generate_chapter(book_code, chapter):
    """Produce the chapter JSON dict."""
    api = tf_api()
    F, T, L = api.F, api.T, api.L
    entry = BOOKS[book_code]
    verse = 1
    data = []
    sense = load_sense_lines(book_code, chapter)
    translit = load_translit(book_code, chapter)
    n_lines_used = 0
    n_tr_attached = 0
    n_tr_skipped = 0
    while True:
        vnode = T.nodeFromSection((entry['bhsa'], chapter, verse))
        if vnode is None:
            break
        words = L.d(vnode, otype='word')
        if not words:
            break
        data.append({'v': verse})
        recs = []
        for w in words:
            rec = word_record(api, w)
            recs.append((rec, consonants_only(rec['txt'])))
        line_breaks = set()
        if sense and verse in sense:
            line_breaks = set(assign_lines(recs, sense[verse]))
            n_lines_used += len(sense[verse])
        if translit and verse in translit:
            if attach_translit(recs, translit[verse]):
                n_tr_attached += 1
            else:
                n_tr_skipped += 1
        for i, (rec, _cons) in enumerate(recs):
            if i in line_breaks:
                data.append({'br': True})
            data.append(rec)
        verse += 1
    if verse == 1:
        raise ValueError(f'No verses found for {book_code} {chapter}')
    return {
        'book': book_code,
        'display': entry['display'],
        'chapter': chapter,
        'sense_lines': bool(sense),
        'translit': bool(translit),
        'tr_attached': n_tr_attached,
        'tr_skipped': n_tr_skipped,
        'data': data,
    }


def write_chapter(book_code, chapter):
    out_dir = os.path.join(BUILD_DIR, book_code)
    os.makedirs(out_dir, exist_ok=True)
    doc = generate_chapter(book_code, chapter)
    out = os.path.join(out_dir, f'{chapter}.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', required=True, choices=sorted(BOOKS))
    ap.add_argument('--chapter', type=int, default=None)
    args = ap.parse_args()
    chapters = [args.chapter] if args.chapter else range(1, BOOKS[args.book]['chapters'] + 1)
    for ch in chapters:
        path = write_chapter(args.book, ch)
        print(f'wrote {path}')


if __name__ == '__main__':
    main()
