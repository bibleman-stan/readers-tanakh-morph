"""Root-radical matcher for the Shoresh layer. Aligns a verb lexeme's
triliteral root (from ETCBC `lem`) onto the surface STEM segment's consonant
skeleton, classifying weak-root losses (assimilation, hollow, III-He apocope,
I-elision, gemination). FAIL-CLOSED: if it can't align with confidence, it
returns conf=0 and NO in-text marking (panel shows the root only).

Importable by generate_chapter.py; runnable standalone as a test harness
against live BHSA anchor fixtures.
"""
import re
import unicodedata

ETCBC_CONS = {
    '>': 'א', 'B': 'ב', 'G': 'ג', 'D': 'ד', 'H': 'ה', 'W': 'ו', 'Z': 'ז',
    'X': 'ח', 'V': 'ט', 'J': 'י', 'K': 'כ', 'L': 'ל', 'M': 'מ', 'N': 'נ',
    'S': 'ס', '<': 'ע', 'P': 'פ', 'Y': 'צ', 'Q': 'ק', 'R': 'ר',
    'F': 'ש', 'C': 'ש', 'T': 'ת',   # F/C (sin/shin) both base to ש
}
_FINAL = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
_DAGESH = 'ּ'
# I-Nun-style assimilators: roots whose R1 assimilates into R2 (dagesh forte).
# נ is the systematic case; לקח behaves like I-Nun; some I-Yod (יצב/נצב) too.
_ASSIM_R1 = {'נ'}             # ל handled only via lqx_exception (red-line safety)
_ELIDE_R1 = {'י', 'ה', 'נ'}   # I-class roots that drop R1 in prefix forms
_HOLLOW_R2 = {'ו', 'י'}
_WEAK_R3 = {'ה', 'י'}


def root_consonants(lem):
    """Hebrew root letters from an ETCBC lexeme (verbs end with '['). Returns
    a list of base consonants, or None if not a clean verbal root."""
    if not lem or not lem.endswith('['):
        return None
    body = lem[:-1]
    cons = [ETCBC_CONS[c] for c in body if c in ETCBC_CONS]
    return cons or None


def _clusters(stem):
    """Split a pointed Hebrew string into grapheme clusters (one base letter
    + its following points/accents). Returns list of (cluster_text, base, has_dagesh)."""
    out = []
    for m in re.finditer(r'[א-ת][֑-ׇ]*', stem):
        cl = m.group(0)
        base = _FINAL.get(cl[0], cl[0])
        out.append((cl, base, _DAGESH in cl))
    return out


def _is_mater(base):
    return base in ('א', 'ה', 'ו', 'י')


def analyze(lem, stem_seg, lqx_exception=False):
    """Return a root-analysis dict for the stem segment, or None.

    Keys: h (Hebrew root), cls (weak-class tags), loss, exp, conf (0|2),
          parts (per-cluster [{t, r}] over the STEM SEG, r in
          rad/r2/mater/''), r2idx (cluster index of R2 or -1).
    conf 2 => parts are safe to render; conf 0 => panel-only (parts omitted).
    """
    root = root_consonants(lem)
    if not root or len(root) not in (3, 4):
        return None
    h = ''.join(root)
    cls = _weak_class(root)
    cl = _clusters(stem_seg)
    bases = [b for (_t, b, _d) in cl]

    geminate = len(root) == 3 and root[1] == root[2]

    # --- attempt full ordered subsequence match (no loss) ---
    m = _subseq(root, bases)
    if m is not None:
        return _build(h, cls, None, None, cl, m, root)

    # --- geminate: R2==R3 may surface as a single doubled letter ---
    if geminate:
        m = _subseq([root[0], root[1]], bases)
        if m is not None:
            # both R2 and R3 point at the single middle/last cluster
            mm = [m[0], m[1], m[1]]
            return _build(h, cls, 'gem',
                          'geminate root — ' + root[1] + ' written once (doubled)',
                          cl, mm, root, r2_at=1)

    # --- one-letter-loss attempts, classified by position ---
    # R1 lost (assimilation or elision in prefixed forms)
    if root[0] in _ELIDE_R1 or (root[0] == 'ל' and lqx_exception):
        m = _subseq(root[1:], bases)
        if m is not None:
            assim = (root[0] in _ASSIM_R1 or (root[0] == 'ל' and lqx_exception)) \
                and any(d for (_t, _b, d) in cl)
            loss = 'assim' if assim else 'elide'
            exp = (root[0] + ' assimilated (dagesh forte in the next letter)'
                   if assim else root[0] + ' elided in the prefix form')
            full = [None, m[0], m[1]] if len(root) == 3 else [None] + list(m)
            return _build(h, cls, loss, exp, cl, full, root)
    # R2 lost (hollow root)
    if root[1] in _HOLLOW_R2:
        m = _subseq([root[0], root[2]], bases)
        if m is not None:
            full = [m[0], None, m[1]]
            return _build(h, cls, 'hollow',
                          'hollow root — middle ' + root[1] + ' not written',
                          cl, full, root)
    # R3 lost (III-He apocope / III-weak)
    if root[2] in _WEAK_R3:
        m = _subseq(root[:2], bases)
        if m is not None:
            full = [m[0], m[1], None]
            return _build(h, cls, 'apoc',
                          'III-' + root[2] + ' — final ' + root[2] + ' dropped',
                          cl, full, root)

    # --- fail closed: root known, no safe in-text mapping ---
    return {'h': h, 'cls': cls, 'conf': 0,
            'exp': 'irregular surface — root shown, letters not marked in text'}


def _subseq(root, bases):
    """Greedy ordered subsequence: every root letter must match a later base,
    in order. Returns list of matched cluster indices, or None."""
    idx = []
    j = 0
    for r in root:
        while j < len(bases) and bases[j] != r:
            j += 1
        if j == len(bases):
            return None
        idx.append(j)
        j += 1
    return idx


def _weak_class(root):
    tags = []
    gutt = set('אהחע')
    if root[0] == 'נ': tags.append('I-Nun')
    if root[0] == 'י': tags.append('I-Yod')
    if root[0] in gutt: tags.append('I-Gutt')
    if root[1] in _HOLLOW_R2: tags.append('Hollow')
    if root[1] in gutt: tags.append('II-Gutt')
    if root[2] == 'ה': tags.append('III-He')
    if root[2] in gutt - {'ה'}: tags.append('III-Gutt')
    if len(root) == 3 and root[1] == root[2]: tags.append('Geminate')
    return tags


def _build(h, cls, loss, exp, clusters, rootmap, root, r2_at=1):
    """rootmap: per-root-letter cluster index (or None). r2_at = which root
    index is R2 (1 normally). Build per-cluster render parts."""
    rad_idx = {ci for ci in rootmap if ci is not None}
    r2_cluster = rootmap[r2_at] if r2_at < len(rootmap) else None
    parts = []
    for ci, (t, base, _d) in enumerate(clusters):
        if ci == r2_cluster:
            r = 'r2'
        elif ci in rad_idx:
            r = 'rad'
        elif _is_mater(base):
            r = 'mater'
        else:
            r = ''
        parts.append({'t': t, 'r': r})
    out = {'h': h, 'cls': cls, 'conf': 2, 'parts': parts,
           'r2idx': r2_cluster if r2_cluster is not None else -1}
    if loss:
        out['loss'] = loss
        out['exp'] = exp
    return out
