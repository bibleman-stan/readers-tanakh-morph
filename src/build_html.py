#!/usr/bin/env python3
"""
Inject a generated Hebrew chapter JSON into the RTL HTML template to produce a
standalone single-file reader page.

Port of the Greek sibling's src/build_html.py (readers-gnt-morph). Differences:
  * The Hebrew chapter JSON keys its `book` field by URL SLUG ("genesis",
    "ruth"), not by display name — so we look BOOKS up directly by slug, and
    there is no display->code translation step.
  * The Hebrew JSON carries glosses INLINE on each word record (`gl`); there is
    no separate top-level `lex` frequency dictionary, so no LEX payload is
    embedded.
  * Template placeholders use the {{NAME}} convention requested for this repo
    ({{TITLE}}, {{BOOK_DISPLAY}}, {{CHAPTER}}, {{NAV_PREV}}, {{NAV_NEXT}},
    {{CH_DATA}}) plus the nav-picker payload placeholders ported from Greek
    ({{BOOK_CODE}}, {{TOTAL_CHAPTERS}}, {{BOOKS_DATA}}, {{BOOK_KEYS}},
    {{VERSE_COUNTS}}).

CLI:
  python src/build_html.py --book genesis --chapter 1
  python src/build_html.py --book ruth --chapter 1 --template ... --out ...
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from books import BOOKS

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_BOOKS_PAYLOAD_CACHE = None
_VERSE_COUNTS_CACHE = None
_VERSE_COUNTS_FILE = os.path.join(_REPO_ROOT, 'build', 'verse_counts.json')


def _books_payload():
    """Small object shipped to the template for the location picker.
    BOOK_KEYS is canonical Tanakh order (Genesis -> 2 Chronicles)."""
    global _BOOKS_PAYLOAD_CACHE
    if _BOOKS_PAYLOAD_CACHE is None:
        ordered = sorted(BOOKS.items(), key=lambda kv: kv[1]['order'])
        _BOOKS_PAYLOAD_CACHE = {
            'books': {code: {'name': meta['display'], 'chapters': meta['chapters']}
                      for code, meta in ordered},
            'keys': [code for code, _ in ordered],
        }
    return _BOOKS_PAYLOAD_CACHE


def _verse_counts():
    """Max-verse-per-chapter map {slug: {chapter: max_verse}} for the location
    picker's verse grid. Persisted to build/verse_counts.json so repeat
    subprocess invocations read the cache instead of rescanning every JSON.
    Delete the file if the build/ JSONs are regenerated with different
    versification."""
    global _VERSE_COUNTS_CACHE
    if _VERSE_COUNTS_CACHE is not None:
        return _VERSE_COUNTS_CACHE

    if os.path.exists(_VERSE_COUNTS_FILE):
        try:
            with open(_VERSE_COUNTS_FILE, 'r', encoding='utf-8') as f:
                _VERSE_COUNTS_CACHE = json.load(f)
                return _VERSE_COUNTS_CACHE
        except (IOError, ValueError):
            pass  # recompute

    counts = {}
    build_root = os.path.join(_REPO_ROOT, 'build')
    for code in BOOKS:
        book_dir = os.path.join(build_root, code)
        if not os.path.isdir(book_dir):
            continue
        counts[code] = {}
        for path in glob.glob(os.path.join(book_dir, '*.json')):
            fname = os.path.basename(path)
            try:
                chapter = int(os.path.splitext(fname)[0])
            except ValueError:
                continue
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
            except (IOError, ValueError):
                continue
            entries = doc.get('data', doc) if isinstance(doc, dict) else doc
            max_v = 0
            for e in entries:
                v = e.get('v') if isinstance(e, dict) else None
                if isinstance(v, int) and v > max_v:
                    max_v = v
            if max_v:
                counts[code][chapter] = max_v
        if not counts[code]:
            del counts[code]

    try:
        os.makedirs(os.path.dirname(_VERSE_COUNTS_FILE), exist_ok=True)
        with open(_VERSE_COUNTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(counts, f, sort_keys=True)
    except IOError:
        pass

    _VERSE_COUNTS_CACHE = counts
    return counts


def build(book, chapter, template_path=None, out_path=None):
    if book not in BOOKS:
        raise SystemExit(f"Unknown book slug: {book!r} (not in books.BOOKS)")
    meta = BOOKS[book]

    data_file = os.path.join(_REPO_ROOT, 'build', book, f'{chapter}.json')
    template_path = template_path or os.path.join(
        _REPO_ROOT, 'templates', 'reader.html')
    out_path = out_path or os.path.join(
        _REPO_ROOT, 'docs', book, f'{chapter}.html')

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    display = meta['display']
    total_chapters = meta['chapters']

    ch_json = json.dumps(data['data'], ensure_ascii=False)
    sense_lines = bool(data.get('sense_lines'))

    payload = _books_payload()
    books_json = json.dumps(payload['books'], ensure_ascii=False)
    keys_json = json.dumps(payload['keys'])
    verse_counts_json = json.dumps(_verse_counts())

    repl = {
        '{{TITLE}}': f'{display} {chapter} — Morpheme Reader',
        '{{BOOK_DISPLAY}}': display,
        '{{BOOK_CODE}}': book,
        '{{CHAPTER}}': str(chapter),
        '{{TOTAL_CHAPTERS}}': str(total_chapters),
        '{{SENSE_LINES}}': 'true' if sense_lines else 'false',
        '{{NAV_PREV}}': f'{chapter - 1}.html' if chapter > 1 else '',
        '{{NAV_NEXT}}': f'{chapter + 1}.html' if chapter < total_chapters else '',
        '{{CH_DATA}}': ch_json,
        '{{BOOKS_DATA}}': books_json,
        '{{BOOK_KEYS}}': keys_json,
        '{{VERSE_COUNTS}}': verse_counts_json,
    }
    for k, v in repl.items():
        html = html.replace(k, v)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    word_count = sum(1 for e in data['data'] if 'txt' in e)
    print(f"Built {out_path}: {len(data['data'])} entries ({word_count} words)")
    return out_path


def main():
    ap = argparse.ArgumentParser(description='Build a single-file RTL Hebrew '
                                             'morpheme-reader chapter page.')
    ap.add_argument('--book', required=True, help='book slug, e.g. genesis')
    ap.add_argument('--chapter', required=True, type=int, help='chapter number')
    ap.add_argument('--template', default=None, help='template path override')
    ap.add_argument('--out', default=None, help='output HTML path override')
    args = ap.parse_args()
    build(args.book, args.chapter, args.template, args.out)


if __name__ == '__main__':
    main()
