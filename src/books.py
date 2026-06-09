#!/usr/bin/env python3
"""
Book registry — single source of truth for BHSA book names, URL slugs,
display names, chapter counts, and sense-line directory codes.

`code` is the URL slug used throughout (lowercase, no spaces).
`bhsa` is the book name as BHSA's T.nodeFromSection expects it.
`sense_code` matches the sibling readers-tanakh repo's directory naming
(at data/text-files/v2/heb/NN-<sense_code>/) — used to locate sense-line
files for colometric layout.
`order` is canonical Tanakh position (Hebrew-Bible ordering, matching the
NN- prefixes in readers-tanakh).
`aramaic` lists chapter ranges containing Aramaic text (verse-level
flagging happens via BHSA's word-level `language` feature; this is the
chapter-level UI hint).
"""

BOOKS = {
    'genesis':       {'display': 'Genesis',         'bhsa': 'Genesis',       'chapters': 50, 'order': 1,  'sense_code': 'genesis'},
    'exodus':        {'display': 'Exodus',          'bhsa': 'Exodus',        'chapters': 40, 'order': 2,  'sense_code': 'exodus'},
    'leviticus':     {'display': 'Leviticus',       'bhsa': 'Leviticus',     'chapters': 27, 'order': 3,  'sense_code': 'leviticus'},
    'numbers':       {'display': 'Numbers',         'bhsa': 'Numeri',        'chapters': 36, 'order': 4,  'sense_code': 'numbers'},
    'deuteronomy':   {'display': 'Deuteronomy',     'bhsa': 'Deuteronomium', 'chapters': 34, 'order': 5,  'sense_code': 'deuteronomy'},
    'joshua':        {'display': 'Joshua',          'bhsa': 'Josua',         'chapters': 24, 'order': 6,  'sense_code': 'joshua'},
    'judges':        {'display': 'Judges',          'bhsa': 'Judices',       'chapters': 21, 'order': 7,  'sense_code': 'judges'},
    '1samuel':       {'display': '1 Samuel',        'bhsa': 'Samuel_I',      'chapters': 31, 'order': 8,  'sense_code': '1samuel'},
    '2samuel':       {'display': '2 Samuel',        'bhsa': 'Samuel_II',     'chapters': 24, 'order': 9,  'sense_code': '2samuel'},
    '1kings':        {'display': '1 Kings',         'bhsa': 'Reges_I',       'chapters': 22, 'order': 10, 'sense_code': '1kings'},
    '2kings':        {'display': '2 Kings',         'bhsa': 'Reges_II',      'chapters': 25, 'order': 11, 'sense_code': '2kings'},
    'isaiah':        {'display': 'Isaiah',          'bhsa': 'Jesaia',        'chapters': 66, 'order': 12, 'sense_code': 'isaiah'},
    'jeremiah':      {'display': 'Jeremiah',        'bhsa': 'Jeremia',       'chapters': 52, 'order': 13, 'sense_code': 'jeremiah'},
    'ezekiel':       {'display': 'Ezekiel',         'bhsa': 'Ezechiel',      'chapters': 48, 'order': 14, 'sense_code': 'ezekiel'},
    'hosea':         {'display': 'Hosea',           'bhsa': 'Hosea',         'chapters': 14, 'order': 15, 'sense_code': 'hosea'},
    'joel':          {'display': 'Joel',            'bhsa': 'Joel',          'chapters': 4,  'order': 16, 'sense_code': 'joel'},
    'amos':          {'display': 'Amos',            'bhsa': 'Amos',          'chapters': 9,  'order': 17, 'sense_code': 'amos'},
    'obadiah':       {'display': 'Obadiah',         'bhsa': 'Obadia',        'chapters': 1,  'order': 18, 'sense_code': 'obadiah'},
    'jonah':         {'display': 'Jonah',           'bhsa': 'Jona',          'chapters': 4,  'order': 19, 'sense_code': 'jonah'},
    'micah':         {'display': 'Micah',           'bhsa': 'Micha',         'chapters': 7,  'order': 20, 'sense_code': 'micah'},
    'nahum':         {'display': 'Nahum',           'bhsa': 'Nahum',         'chapters': 3,  'order': 21, 'sense_code': 'nahum'},
    'habakkuk':      {'display': 'Habakkuk',        'bhsa': 'Habakuk',       'chapters': 3,  'order': 22, 'sense_code': 'habakkuk'},
    'zephaniah':     {'display': 'Zephaniah',       'bhsa': 'Zephania',      'chapters': 3,  'order': 23, 'sense_code': 'zephaniah'},
    'haggai':        {'display': 'Haggai',          'bhsa': 'Haggai',        'chapters': 2,  'order': 24, 'sense_code': 'haggai'},
    'zechariah':     {'display': 'Zechariah',       'bhsa': 'Sacharia',      'chapters': 14, 'order': 25, 'sense_code': 'zechariah'},
    'malachi':       {'display': 'Malachi',         'bhsa': 'Maleachi',      'chapters': 3,  'order': 26, 'sense_code': 'malachi'},
    'psalms':        {'display': 'Psalms',          'bhsa': 'Psalmi',        'chapters': 150,'order': 27, 'sense_code': 'psalms'},
    'job':           {'display': 'Job',             'bhsa': 'Iob',           'chapters': 42, 'order': 28, 'sense_code': 'job'},
    'proverbs':      {'display': 'Proverbs',        'bhsa': 'Proverbia',     'chapters': 31, 'order': 29, 'sense_code': 'proverbs'},
    'ruth':          {'display': 'Ruth',            'bhsa': 'Ruth',          'chapters': 4,  'order': 30, 'sense_code': 'ruth'},
    'songofsongs':   {'display': 'Song of Songs',   'bhsa': 'Canticum',      'chapters': 8,  'order': 31, 'sense_code': 'songofsongs'},
    'ecclesiastes':  {'display': 'Ecclesiastes',    'bhsa': 'Ecclesiastes',  'chapters': 12, 'order': 32, 'sense_code': 'ecclesiastes'},
    'lamentations':  {'display': 'Lamentations',    'bhsa': 'Threni',        'chapters': 5,  'order': 33, 'sense_code': 'lamentations'},
    'esther':        {'display': 'Esther',          'bhsa': 'Esther',        'chapters': 10, 'order': 34, 'sense_code': 'esther'},
    'daniel':        {'display': 'Daniel',          'bhsa': 'Daniel',        'chapters': 12, 'order': 35, 'sense_code': 'daniel',
                      'aramaic': [(2, 7)]},
    'ezra':          {'display': 'Ezra',            'bhsa': 'Esra',          'chapters': 10, 'order': 36, 'sense_code': 'ezra',
                      'aramaic': [(4, 7)]},
    'nehemiah':      {'display': 'Nehemiah',        'bhsa': 'Nehemia',       'chapters': 13, 'order': 37, 'sense_code': 'nehemiah'},
    '1chronicles':   {'display': '1 Chronicles',    'bhsa': 'Chronica_I',    'chapters': 29, 'order': 38, 'sense_code': '1chronicles'},
    '2chronicles':   {'display': '2 Chronicles',    'bhsa': 'Chronica_II',   'chapters': 36, 'order': 39, 'sense_code': '2chronicles'},
}

# Hebrew binyanim + Aramaic stems, as BHSA `vs` values → display info.
# Color keys map to CSS classes in the template.
BINYANIM = {
    # Hebrew
    'qal':  {'display': 'Qal',      'color': 'qal'},
    'nif':  {'display': 'Nifal',    'color': 'nif'},
    'piel': {'display': 'Piel',     'color': 'piel'},
    'pual': {'display': 'Pual',     'color': 'pual'},
    'hif':  {'display': 'Hifil',    'color': 'hif'},
    'hof':  {'display': 'Hofal',    'color': 'hof'},
    'hit':  {'display': 'Hitpael',  'color': 'hit'},
    # Minor Hebrew stems (bucketed visually as "minor" but labeled precisely)
    'hsht': {'display': 'Hishtafel','color': 'minor'},
    'hotp': {'display': 'Hotpaal',  'color': 'minor'},
    'nit':  {'display': 'Nitpael',  'color': 'minor'},
    'poal': {'display': 'Poal',     'color': 'minor'},
    'poel': {'display': 'Poel',     'color': 'minor'},
    'tif':  {'display': 'Tifal',    'color': 'minor'},
    'pasq': {'display': 'Passive Qal', 'color': 'minor'},
    'htpo': {'display': 'Hitpoel',  'color': 'minor'},
    # Aramaic stems
    'peal': {'display': 'Peal',     'color': 'qal'},
    'peil': {'display': 'Peil',     'color': 'qal'},
    'pael': {'display': 'Pael',     'color': 'piel'},
    'haf':  {'display': 'Hafel',    'color': 'hif'},
    'afel': {'display': 'Afel',     'color': 'hif'},
    'shaf': {'display': 'Shafel',   'color': 'minor'},
    'htpe': {'display': 'Hitpeel',  'color': 'hit'},
    'htpa': {'display': 'Hitpaal',  'color': 'hit'},
    'etpa': {'display': 'Etpaal',   'color': 'hit'},
    'etpe': {'display': 'Etpeel',   'color': 'hit'},
}

# BHSA `vt` (verbal tense) values → display names
TENSES = {
    'perf': 'perfect (qatal)',
    'impf': 'imperfect (yiqtol)',
    'wayq': 'wayyiqtol',
    'impv': 'imperative',
    'infa': 'infinitive absolute',
    'infc': 'infinitive construct',
    'ptca': 'participle (active)',
    'ptcp': 'participle (passive)',
}
