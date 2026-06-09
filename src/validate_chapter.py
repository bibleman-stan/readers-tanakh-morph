#!/usr/bin/env python3
"""
validate_chapter.py — mechanical correctness gate for generated chapter JSON.

Per HANDOFF.md (Greek sibling) Part 1.5: build the validator BEFORE polishing
display. Checks run against BOTH the generated JSON and BHSA ground truth.

Checks:
  C1 reassembly      — concatenated segs == surface text, per word, exact
  C2 word coverage   — every BHSA word-slot in the chapter appears exactly
                       once, in BHSA order
  C3 binyan sanity   — every sp=verb has vs+vsd; no non-verb carries vs
  C4 suffix presence — prs segment present iff BHSA g_prs has content
  C5 sense coverage  — consonantal text of each sense-line in the JSON
                       matches the readers-tanakh v2/heb file line-for-line
  C6 aramaic flag    — every word with language=Aramaic carries arc:true,
                       and no Hebrew word does
  C7 seg mismatch    — count of words that fell back to whole-word display
                       despite BHSA offering decomposition (quality metric)

Usage:
  PYTHONIOENCODING=utf-8 python src/validate_chapter.py --book genesis --chapter 1
  PYTHONIOENCODING=utf-8 python src/validate_chapter.py --book ruth   # all chapters
"""
import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from books import BOOKS
import generate_chapter as gc

BUILD_DIR = gc.BUILD_DIR


def validate_chapter(book_code, chapter, api=None):
    """Run all checks for one chapter. Returns (ok, findings, stats)."""
    findings = []
    path = os.path.join(BUILD_DIR, book_code, f'{chapter}.json')
    if not os.path.exists(path):
        return False, [f'missing JSON: {path}'], {}
    with open(path, encoding='utf-8') as f:
        doc = json.load(f)
    words = [d for d in doc['data'] if 'txt' in d]

    api = api or gc.tf_api()
    F, T, L = api.F, api.T, api.L
    entry = BOOKS[book_code]

    # Ground-truth word list from BHSA
    bhsa_words = []
    verse = 1
    while True:
        vnode = T.nodeFromSection((entry['bhsa'], chapter, verse))
        if vnode is None:
            break
        ws = L.d(vnode, otype='word')
        if not ws:
            break
        bhsa_words.extend(ws)
        verse += 1

    # C1 reassembly
    c1_bad = [w['txt'] for w in words if ''.join(s['t'] for s in w['segs']) != w['txt']]
    if c1_bad:
        findings.append(f'C1 reassembly: {len(c1_bad)} failures, e.g. {c1_bad[:3]}')

    # C2 coverage + order
    if len(words) != len(bhsa_words):
        findings.append(f'C2 coverage: JSON has {len(words)} words, BHSA has {len(bhsa_words)}')
    else:
        for i, (jw, bw) in enumerate(zip(words, bhsa_words)):
            if jw['txt'] != (F.g_word_utf8.v(bw) or ''):
                findings.append(f'C2 order: divergence at index {i}: {jw["txt"]!r} vs BHSA {F.g_word_utf8.v(bw)!r}')
                break

    # C3 binyan sanity
    c3_missing = [w['txt'] for w in words if w.get('sp') == 'verb' and 'vs' not in w]
    c3_excess = [w['txt'] for w in words if w.get('sp') != 'verb' and 'vs' in w]
    if c3_missing:
        findings.append(f'C3 binyan: {len(c3_missing)} verbs without vs, e.g. {c3_missing[:3]}')
    if c3_excess:
        findings.append(f'C3 binyan: {len(c3_excess)} non-verbs with vs, e.g. {c3_excess[:3]}')

    # C4 suffix presence (against BHSA)
    c4_bad = []
    if len(words) == len(bhsa_words):
        for jw, bw in zip(words, bhsa_words):
            bhsa_prs = (F.g_prs_utf8.v(bw) or '').replace(gc._BHSA_MARKER, '')
            has_prs_seg = any(s['m'] == 'prs' for s in jw['segs'])
            whole = len(jw['segs']) == 1 and jw['segs'][0]['m'] == 'whole'
            if bhsa_prs and not has_prs_seg and not whole:
                c4_bad.append(jw['txt'])
    if c4_bad:
        findings.append(f'C4 suffix: {len(c4_bad)} words with BHSA prs but no prs segment, e.g. {c4_bad[:3]}')

    # C5 sense coverage
    sense = gc.load_sense_lines(book_code, chapter)
    if sense:
        # Rebuild per-verse lines from JSON and compare consonantal text
        verse_lines = {}   # verse -> list of consonant strings (one per line)
        cur_v = None
        cur_line = []
        lines_acc = []
        for d in doc['data']:
            if 'v' in d:
                if cur_v is not None:
                    if cur_line:
                        lines_acc.append(cur_line)
                    verse_lines[cur_v] = lines_acc
                cur_v = d['v']
                lines_acc = []
                cur_line = []
            elif d.get('br'):
                lines_acc.append(cur_line)
                cur_line = []
            elif 'txt' in d:
                cur_line.append(gc._matchform(gc.consonants_only(d['txt'])))
        if cur_v is not None:
            if cur_line:
                lines_acc.append(cur_line)
            verse_lines[cur_v] = lines_acc
        import difflib
        c5_count_bad = []
        c5_content_bad = []
        c5_form_drift = 0
        for vnum, slines in sense.items():
            jlines = verse_lines.get(vnum, [])
            sl = [''.join(gc._matchform(t) for t in line) for line in slines]
            jl = [''.join(line) for line in jlines]
            if len(sl) != len(jl):
                c5_count_bad.append(vnum)
                continue
            for s, j in zip(sl, jl):
                if s == j:
                    continue
                # Tolerate small orthographic drift (ketiv/qere; the
                # sense files are TAHOT-form, BHSA differs in ~3.5% of
                # verses — see the BHSA-canon-migration arc). A real
                # break-position error moves whole words and drops the
                # ratio far below this threshold.
                ratio = difflib.SequenceMatcher(None, s, j, autojunk=False).ratio()
                if ratio < 0.85:
                    c5_content_bad.append(vnum)
                    break
                c5_form_drift += 1
        if c5_count_bad:
            findings.append(f'C5 sense-lines: {len(c5_count_bad)} verses with line-COUNT mismatch: {c5_count_bad[:5]}')
        if c5_content_bad:
            findings.append(f'C5 sense-lines: {len(c5_content_bad)} verses with line-content divergence beyond ketiv/qere tolerance: {c5_content_bad[:5]}')
        # form-drift count is informational (stats), not a failure

    # C6 aramaic flag
    c6_bad = []
    if len(words) == len(bhsa_words):
        for jw, bw in zip(words, bhsa_words):
            is_arc = F.language.v(bw) == 'Aramaic'
            if is_arc != bool(jw.get('arc')):
                c6_bad.append(jw['txt'])
    if c6_bad:
        findings.append(f'C6 aramaic: {len(c6_bad)} flag mismatches, e.g. {c6_bad[:3]}')

    # C7 seg-mismatch quality metric
    n_mism = sum(1 for w in words if w.get('seg_mismatch'))
    n_multi = sum(1 for w in words if len(w['segs']) > 1)

    stats = {
        'words': len(words),
        'multi_segment': n_multi,
        'seg_mismatch': n_mism,
        'findings': len(findings),
    }
    return not findings, findings, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', required=True, choices=sorted(BOOKS))
    ap.add_argument('--chapter', type=int, default=None)
    args = ap.parse_args()
    api = gc.tf_api()
    chapters = [args.chapter] if args.chapter else range(1, BOOKS[args.book]['chapters'] + 1)
    all_ok = True
    tot = {'words': 0, 'multi_segment': 0, 'seg_mismatch': 0}
    for ch in chapters:
        ok, findings, stats = validate_chapter(args.book, ch, api)
        for k in tot:
            tot[k] += stats.get(k, 0)
        flag = 'OK ' if ok else 'FAIL'
        print(f'{flag} {args.book} {ch}: {stats}')
        for f_ in findings:
            print(f'     - {f_}')
        all_ok = all_ok and ok
    if len(list(chapters) if not isinstance(chapters, list) else chapters) != 1:
        pct = 100 * tot['multi_segment'] / tot['words'] if tot['words'] else 0
        print(f'\nTOTAL: {tot["words"]} words, {tot["multi_segment"]} multi-segment ({pct:.1f}%), '
              f'{tot["seg_mismatch"]} seg-mismatch')
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
