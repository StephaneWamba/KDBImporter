from __future__ import annotations
import argparse
import collections
import pathlib
import sys
from typing import List, Tuple

# import fitz  # PyMuPDF
import spacy
from spacy.language import Language
from spacy.tokens import Doc

# ----------------------------------------------------------------------------
# Configuration – default PDF path
# ----------------------------------------------------------------------------

DEFAULT_PDF_PATH = pathlib.Path(r"C:\Users\DELL\Downloads\2406.13258v3.pdf")

# ----------------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------------


def _load_spacy_model() -> Language:
    """Load the best available English spaCy model with word vectors."""
    candidates: List[str] = [
        "en_core_web_lg",
        "en_core_web_md",
        "en_core_web_sm",
    ]
    for name in candidates:
        try:
            nlp = spacy.load(name)  # type: ignore[arg-type]
            if nlp.vocab.vectors_length == 0:
                print(
                    f"[warning] The spaCy model '{name}' has no word vectors; "
                    "similarity scores may be unreliable.",
                    file=sys.stderr,
                )
            return nlp
        except OSError:
            continue
    raise SystemExit(
        "No suitable spaCy English model found. Please install one, e.g.\n"
        "    python -m spacy download en_core_web_lg"
    )


# def extract_text(pdf_path: pathlib.Path) -> str:
#     """Concatenate text from all pages of *pdf_path*."""
#     doc = fitz.open(pdf_path)
#     return "\n".join(page.get_text() for page in doc)


def _is_candidate(token) -> bool:
    """Return True if *token* is a non‑stopword noun or proper noun."""
    return (
        token.pos_ in {"NOUN", "PROPN"}
        and not token.is_stop
        and token.is_alpha
        and len(token.text) > 2
    )


def extract_candidates(doc: Doc) -> List[str]:
    """Return lowercase noun lemmas and noun‑chunk phrases from *doc*."""
    single_words = [t.lemma_.lower() for t in doc if _is_candidate(t)]
    phrases = [
        chunk.text.lower()
        for chunk in doc.noun_chunks
        if not any(tok.is_stop for tok in chunk) and len(chunk) <= 4
    ]
    return single_words + phrases


def rank_keywords(
    candidates: List[str],
    subject_doc: Doc,
    nlp: Language,
    topn: int,
) -> List[Tuple[str, float]]:
    """Rank *candidates* by (frequency × semantic similarity)."""
    freq = collections.Counter(candidates)
    scored = {
        phrase: count * nlp(phrase).similarity(subject_doc)
        for phrase, count in freq.items()
    }
    ranked = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)
    return ranked[:topn]


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:  # type: ignore[no-any-unimported]
    p = argparse.ArgumentParser(description="Keyword extractor (spaCy + PDF)")
    p.add_argument(
        "--pdf",
        type=pathlib.Path,
        default=DEFAULT_PDF_PATH,
        help="PDF file path (default: %(default)s)",
    )
    p.add_argument("--subject", default="post quantum cryptography",
                   help="Context/subject focus phrase (default: %(default)s)")

    p.add_argument(
        "--topn",
        type=int,
        default=30,
        help="Number of keywords to return (default=20)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if not args.pdf.is_file():
        raise SystemExit(f"PDF not found: {args.pdf}")

    nlp = _load_spacy_model()
    text = ""

    # pdf_text = extract_text(args.pdf)
    pdf_doc = nlp(text)
    candidates = extract_candidates(pdf_doc)

    subject_doc = nlp(args.subject.lower())
    top_keywords = rank_keywords(candidates, subject_doc, nlp, args.topn)

    print(f"Top {len(top_keywords)} keywords relevant to '{args.subject}':\n")
    for kw, score in top_keywords:
        print(f"  {kw:<40} {score:>.4f}")

import spacy, sys
for m in ("en_core_web_lg", "en_core_web_md", "en_core_web_sm"):
    try:
        spacy.load(m)
    except OSError:
        print("✘", m, "NOT FOUND")


if __name__ == "__main__":
    main()

