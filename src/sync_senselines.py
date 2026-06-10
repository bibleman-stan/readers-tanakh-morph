#!/usr/bin/env python3
"""
sync_senselines.py — Detect and regenerate chapters whose sense-line
source (in the sibling readers-tanakh repo) has changed since we last built.

The morph-reader consumes sense-line files from
  C:/Users/bibleman/repos/readers-tanakh/data/text-files/v2/heb/
  (overridable via SENSE_LINES_DIR env var)
This is readers-tanakh's LIVE v1.5 binding-rule layer (dir name historical).
If readers-tanakh ever moves its live dir, update BOTH this constant and
generate_chapter.py — the Greek sibling shipped stale line-breaks for two
weeks on a dead path (fixed 2026-06-06).

Uses SHA-256 hashes (not mtimes — Windows/git resets mtimes on clones)
stored in build/sense_hashes.json. Any mismatch means the chapter is stale.

Usage:
  PYTHONIOENCODING=utf-8 python src/sync_senselines.py            # report only
  PYTHONIOENCODING=utf-8 python src/sync_senselines.py --regen
  PYTHONIOENCODING=utf-8 python src/sync_senselines.py --regen --book ruth
"""
import argparse
import hashlib
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from books import BOOKS
import generate_chapter as gc

_REPO_ROOT = os.path.dirname(_HERE)
_MANIFEST = os.path.join(_REPO_ROOT, 'build', 'sense_hashes.json')


def sense_line_path(book_code, chapter):
    entry = BOOKS.get(book_code)
    if not entry:
        return None
    sc = entry['sense_code']
    if not os.path.isdir(gc.SENSE_LINES_DIR):
        return None
    for d in os.listdir(gc.SENSE_LINES_DIR):
        parts = d.split('-', 1)
        if len(parts) == 2 and parts[1] == sc:
            return os.path.join(gc.SENSE_LINES_DIR, d, f'{sc}-{chapter:02d}.txt')
    return None


def file_sha(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load_manifest():
    if os.path.exists(_MANIFEST):
        with open(_MANIFEST, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_manifest(m):
    os.makedirs(os.path.dirname(_MANIFEST), exist_ok=True)
    with open(_MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(m, f, indent=1, sort_keys=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--regen', action='store_true')
    ap.add_argument('--book', choices=sorted(BOOKS), default=None)
    args = ap.parse_args()

    manifest = load_manifest()
    book_codes = [args.book] if args.book else sorted(BOOKS, key=lambda b: BOOKS[b]['order'])

    stale = []
    for code in book_codes:
        for ch in range(1, BOOKS[code]['chapters'] + 1):
            key = f'{code}/{ch}'
            sha = file_sha(sense_line_path(code, ch))
            if sha is None:
                continue
            if manifest.get(key) != sha:
                stale.append((code, ch, sha))

    if not stale:
        print('All chapters in sync with sense-line sources.')
        return

    print(f'{len(stale)} stale chapter(s):')
    for code, ch, _ in stale[:30]:
        print(f'  {code}/{ch}')
    if len(stale) > 30:
        print(f'  … and {len(stale) - 30} more')

    if not args.regen:
        print('\nRun with --regen to rebuild these.')
        return

    import build_html
    import validate_chapter as vc
    api = gc.tf_api()
    t0 = time.time()
    n_fail = 0
    for code, ch, sha in stale:
        gc.write_chapter(code, ch)
        ok, findings, _stats = vc.validate_chapter(code, ch, api)
        if not ok:
            n_fail += 1
            print(f'  VALIDATOR FAIL {code}/{ch}: {findings}')
            continue   # do not ship an invalid chapter; manifest not updated
        build_html.build(code, ch)
        manifest[f'{code}/{ch}'] = sha
    save_manifest(manifest)
    print(f'\nRegenerated {len(stale) - n_fail}/{len(stale)} in {time.time()-t0:.1f}s. '
          f'{"VALIDATOR FAILURES: " + str(n_fail) if n_fail else "Manifest updated."}')
    if n_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
