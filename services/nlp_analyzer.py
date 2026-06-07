from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    _nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("Run: python -m spacy download en_core_web_sm")

_KEYWORD_POS = {"NOUN", "PROPN", "ADJ"}
_MIN_KW_LEN  = 3
TOP_JD_KEYWORDS = 40
TOP_RESULTS     = 20


@dataclass
class AnalysisResult:
    similarity_score:  float
    jd_keywords:       List[str]
    matching_keywords: List[str]
    missing_keywords:  List[str]
    suggestions:       List[str] = field(default_factory=list)


def _clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_spacy_keywords(text: str) -> List[str]:
    doc = _nlp(text[:100_000])
    keywords: set[str] = set()
    for token in doc:
        if token.pos_ in _KEYWORD_POS and not token.is_stop and not token.is_punct and len(token.text) >= _MIN_KW_LEN:
            keywords.add(token.lemma_.lower())
    for chunk in doc.noun_chunks:
        phrase = chunk.text.lower().strip()
        if len(phrase) >= _MIN_KW_LEN:
            keywords.add(phrase)
    return sorted(keywords)


def _tfidf_rank_keywords(resume_text: str, jd_text: str) -> tuple[float, List[str]]:
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )
    tfidf_matrix  = vectorizer.fit_transform([_clean(resume_text), _clean(jd_text)])
    similarity    = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
    feature_names = vectorizer.get_feature_names_out()
    jd_weights    = tfidf_matrix[1].toarray().flatten()
    ranked        = jd_weights.argsort()[::-1]
    ranked_keywords = [feature_names[i] for i in ranked if jd_weights[i] > 0][:TOP_JD_KEYWORDS]
    return similarity, ranked_keywords


def _diff_keywords(jd_keywords: List[str], resume_text: str) -> tuple[List[str], List[str]]:
    cleaned = _clean(resume_text)
    matching, missing = [], []
    for kw in jd_keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, cleaned):
            matching.append(kw)
        else:
            missing.append(kw)
    return matching[:TOP_RESULTS], missing[:TOP_RESULTS]


def analyse(resume_text: str, jd_text: str) -> AnalysisResult:
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty. Please complete your career profile first.")
    if not jd_text or not jd_text.strip():
        raise ValueError("Job description text is empty.")

    similarity_raw, jd_tfidf_keywords = _tfidf_rank_keywords(resume_text, jd_text)
    matching, missing = _diff_keywords(jd_tfidf_keywords, resume_text)

    return AnalysisResult(
        similarity_score=round(similarity_raw * 100, 1),
        jd_keywords=jd_tfidf_keywords,
        matching_keywords=matching,
        missing_keywords=missing,
    )