#!/usr/bin/env python3
"""
bulk_generate.py — regenerate chapter JSON + HTML for the whole Tanakh
(or one book), validator-gated.

The BHSA Text-Fabric corpus loads once per process (~30 s); per-chapter
extraction is fast after that.

Usage:
  PYTHONIOENCODING=utf-8 python src/bulk_generate.py            # all 39 books
  PYTHONIOENCODING=utf-8 python src/bulk_generate.py --book ruth
  PYTHONIOENCODING=utf-8 python src/bulk_generate.py --no-html  # JSON only
"""
import argparse
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from books import BOOKS
import generate_chapter as gc
import validate_chapter as vc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', choices=sorted(BOOKS), default=None)
    ap.add_argument('--no-html', action='store_true')
    args = ap.parse_args()

    book_codes = [args.book] if args.book else sorted(BOOKS, key=lambda b: BOOKS[b]['order'])
    t0 = time.time()
    api = gc.tf_api()
    print(f'TF loaded in {time.time()-t0:.1f}s')

    if not args.no_html:
        import build_html

    n_ch = 0
    n_fail = 0
    fail_list = []
    t1 = time.time()
    for code in book_codes:
        entry = BOOKS[code]
        for ch in range(1, entry['chapters'] + 1):
            gc.write_chapter(code, ch)
            ok, findings, stats = vc.validate_chapter(code, ch, api)
            n_ch += 1
            if not ok:
                n_fail += 1
                fail_list.append((code, ch, findings))
            if not args.no_html:
                build_html.build(code, ch)
        print(f'  {code}: {entry["chapters"]} chapters done '
              f'({n_ch} total, {time.time()-t1:.0f}s)')

    print(f'\nDone: {n_ch} chapters in {time.time()-t1:.1f}s '
          f'(total incl. TF load: {time.time()-t0:.1f}s)')
    if n_fail:
        print(f'VALIDATOR FAILURES: {n_fail} chapters')
        for code, ch, findings in fail_list[:20]:
            print(f'  {code} {ch}:')
            for f_ in findings:
                print(f'    - {f_}')
        sys.exit(1)
    print('All chapters validator-clean.')


if __name__ == '__main__':
    main()
