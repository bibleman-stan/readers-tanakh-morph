# Data attribution

This project consumes the following external data:

## BHSA (Biblia Hebraica Stuttgartensia Amstelodamensis)

- **Source**: ETCBC (Eep Talstra Centre for Bible and Computer), Vrije
  Universiteit Amsterdam — https://github.com/ETCBC/bhsa
- **Version**: 2021, via Text-Fabric
- **License**: CC BY-NC 4.0
- **Used for**: Hebrew text (g_word_utf8), morpheme segmentation
  (g_pfm/g_vbs/g_lex/g_vbe/g_nme/g_prs/g_uvf), morphology (vs, vt, sp, ps,
  gn, nu, st), lexeme glosses (gloss), language tagging (Hebrew/Aramaic)
- **Local path**: vendored at `~/repos/biblical-corpora/bhsa/` (not in this
  repo)

## Tanakh Reader sense-lines

- **Source**: the sibling `readers-tanakh` project (tanakh-reader.com)
- **Used for**: colometric line-break layout (ATU lines), consumed read-only
  from `readers-tanakh/data/text-files/v2/heb/`

## Text-Fabric

- **Source**: Dirk Roorda et al., https://github.com/annotation/text-fabric
- **License**: MIT
- **Used as**: the corpus-access library for BHSA
