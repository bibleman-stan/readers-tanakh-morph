#!/usr/bin/env python3
"""
Known TAHOT-vs-BHSA textual divergences — C5 sense-line whitelist.

The readers-tanakh sense files are TAHOT-form; this reader's text is BHSA
(= MT). In these verses the two texts genuinely diverge beyond the
ketiv/qere similarity tolerance: whole-word ketiv/qere swaps (Job 6:29
washuvu/washvi, 2Kgs 18:27 // Isa 36:12 euphemism qere), MT minuses where
TAHOT carries a plus (Gen 4:8 "let us go into the field", 1Sam 13:1 regnal
number, 1Sam 14:41 LXX plus, Ps 145:13 nun-verse line, Neh 7:67), and
Chronicles geographic-list plusses.

The C5 validator check SKIPS line-content comparison for these verses
(line-break assignment still happens via the difflib opcode aligner, which
degrades gracefully). Generated 2026-06-06 from the corpus-wide triage;
each entry carries its observed diff. When the BHSA-canon-migration arc
lands in readers-tanakh, regenerate this list -- most entries should
disappear.
"""

# (book_code, chapter, verse) -> observed divergence at triage time
KNOWN_DIVERGENCES = {
    ('1chronicles', 4, 13): 'sense: חתתומעונתי | json : חתת',
    ('1chronicles', 6, 12): 'sense: אלקנהבנוושמואלבנו | json : אלקנהבנו',
    ('1chronicles', 6, 44): 'sense: ואתעשןואתמגרשיה | json : ואתעשן',
    ('1chronicles', 6, 62): 'sense: אתיקנעםואתמגרשיהאתקרתהואתמגרשיהאתרמונו | json : אתרמונו',
    ('1chronicles', 8, 30): 'sense: ובעלונרונדב | json : ובעלונדב',
    ('1chronicles', 9, 41): 'sense: ומלךותחרעואחז | json : ומלךותחרע',
    ('1chronicles', 25, 9): 'sense: ואחיוובניושניםעשרגדליהוהשניהואואחיוובניו | json : גדליהוהשניהואואחיוובניו',
    ('1samuel', 2, 16): 'sense: לא | json : לו',
    ('1samuel', 5, 9): 'sense: וישתרולהםטחרים | json : וישתרולהםעפלים',
    ('1samuel', 10, 1): 'sense: הלואכימשחךיהוהלנגידעלעמועלישראלואתהתעצרבעםיהוהואתהתושיענומידאיביומסביבוזהלךהאותמ | json : הלואכימשחךיהוהעלנחלתולנגיד',
    ('1samuel', 13, 1): 'sense: בןשלשיםשנה | json : בןשנה | sense: וארבעיםושתישניםמלךעלישראל',
    ('1samuel', 13, 15): 'LINE-COUNT sense=6 json=4',
    ('1samuel', 14, 41): 'sense: אלהיישראל | json : אלהי | sense: למהלאעניתאתעבדךהיוםאםישביאוביונתןבניהעוןהזהיהוהאלהיישראלהבהאוריםואםישנוהעוןהזהבע',
    ('2kings', 8, 10): 'sense: אמרלו | json : אמרלא',
    ('2kings', 9, 33): 'sense: שמטוה | json : שמטהו',
    ('2kings', 11, 2): 'sense: המומתים | json : הממותתים',
    ('2kings', 18, 27): 'sense: הישביםעלהחמהלאכלאתצואתםולשתותאתמימירגליהםעמכם | json : הישביםעלהחמהלאכלאתחריהםולשתותאתשיניהםעמכם',
    ('2kings', 25, 3): 'sense: בחדשהרביעיבתשעהלחדשויחזקהרעבבעיר | json : בתשעהלחדשויחזקהרעבבעיר',
    ('2samuel', 13, 34): 'LINE-COUNT sense=7 json=4',
    ('2samuel', 14, 30): 'sense: והציתוהבאש | json : והוצתיהבאש',
    ('2samuel', 15, 8): 'sense: ועבדתיאתיהוהבחברון | json : ועבדתיאתיהוה',
    ('2samuel', 16, 10): 'sense: כהיקלל | json : כייקלל',
    ('2samuel', 16, 18): 'sense: לואהיה | json : לאאהיה',
    ('daniel', 2, 33): 'sense: ומנהין | json : ומנהון',
    ('daniel', 3, 7): 'sense: וסופניהוכלזניזמרא | json : וכלזניזמרא',
    ('daniel', 9, 24): 'sense: ולהתםחטאת | json : ולחתםחטאות',
    ('deuteronomy', 28, 30): 'sense: ואישאחרישכבנה | json : ואישאחרישגלנה',
    ('deuteronomy', 30, 16): 'sense: אםתשמעאלמצותיהוהאלהיךאשראנכימצוךהיום | json : אשראנכימצוךהיום',
    ('ecclesiastes', 9, 2): 'LINE-COUNT sense=8 json=7',
    ('esther', 3, 7): 'sense: ומחדשלחדשויפלהגורלעלשלושהעשריוםלחדששניםעשרהואחדשאדר | json : ומחדשלחדששניםעשרהואחדשאדר',
    ('ezekiel', 7, 21): 'sense: וחללוהו | json : וחללה',
    ('ezekiel', 14, 4): 'sense: בא | json : בה',
    ('ezra', 8, 5): 'sense: מבניזתואשכניה | json : מבנישכניה',
    ('genesis', 4, 8): 'sense: נלכההשדהויהי | json : ויהי',
    ('isaiah', 13, 16): 'sense: ונשיהםתשכבנה | json : ונשיהםתשגלנה',
    ('isaiah', 36, 12): 'sense: הישביםעלהחומהלאכלאתצואתםולשתותאתמימירגליהםעמכם | json : הישביםעלהחומהלאכלאתחראיהםולשתותאתשיניהםעמכם',
    ('jeremiah', 2, 20): 'sense: לאאעבור | json : לאאעבד',
    ('jeremiah', 3, 2): 'sense: איפהלאשכבת | json : איפהלאשגלת',
    ('jeremiah', 6, 21): 'sense: ואבדו | json : יאבדו',
    ('jeremiah', 13, 20): 'sense: וראו | json : וראי',
    ('jeremiah', 21, 9): 'sense: וחיה | json : יחיה',
    ('jeremiah', 29, 23): 'sense: היודע | json : הוידע',
    ('jeremiah', 39, 12): 'sense: כי | json : כיאם',
    ('jeremiah', 48, 20): 'sense: הילילו | json : הילילי | sense: וזעקו',
    ('jeremiah', 51, 3): 'sense: אלידרך | json : אלידרךידרך',
    ('jeremiah', 51, 34): 'sense: אכלני | json : אכלנו',
    ('job', 6, 29): 'sense: ושובו | json : ושבי',
    ('job', 10, 20): 'sense: וחדל | json : יחדל',
    ('job', 13, 15): 'sense: לואיחל | json : לאאיחל',
    ('joshua', 6, 13): 'sense: הלוך | json : הולך',
    ('judges', 16, 13): 'sense: עםהמסכתותקעתביתדאלהקירוחליתיוהייתיכאחדהאדם | json : עםהמסכת',
    ('judges', 16, 14): 'LINE-COUNT sense=7 json=5',
    ('judges', 19, 13): 'sense: לכה | json : לך',
    ('lamentations', 4, 17): 'sense: עודינו | json : עודינה',
    ('nehemiah', 5, 9): 'sense: ואומר | json : ויאמר',
    ('nehemiah', 7, 67): 'LINE-COUNT sense=5 json=4',
    ('nehemiah', 12, 14): 'sense: למליכויונתן | json : למלוכייונתן',
    ('proverbs', 17, 27): 'sense: יקררוח | json : וקררוח',
    ('proverbs', 22, 3): 'sense: ונסתר | json : ויסתר',
    ('proverbs', 23, 5): 'sense: כנשריעוףהשמים | json : כנשרועיףהשמים',
    ('proverbs', 31, 4): 'sense: אישכר | json : אושכר',
    ('psalms', 25, 21): 'sense: קויתיךיהוה | json : קויתיך',
    ('psalms', 60, 7): 'sense: וענני | json : ועננו',
    ('psalms', 145, 13): 'sense: וממשלתךבכלדורודורנאמןיהוהבכלדבריווחסידבכלמעשיו | json : וממשלתךבכלדורודור',
    ('zechariah', 14, 2): 'sense: והנשיםתשכבנה | json : והנשיםתשגלנה',
}
