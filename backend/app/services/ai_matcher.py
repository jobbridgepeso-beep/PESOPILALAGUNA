"""
AI Matcher service for the JobBridge application.

Uses TF-IDF vectorization and cosine similarity (scikit-learn) to compute
match scores between jobseeker profiles and job vacancies.

Requirements: 7.1, 7.2, 7.3, 7.4
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _build_profile_text(profile: dict[str, Any]) -> str:
    """Concatenate jobseeker skills and experience into a single text string."""
    parts: list[str] = []

    skills = profile.get("skills") or []
    if isinstance(skills, list):
        parts.append(" ".join(str(s) for s in skills))

    experience = profile.get("experience") or []
    if isinstance(experience, list):
        for exp in experience:
            if isinstance(exp, dict):
                parts.append(exp.get("position", ""))
                parts.append(exp.get("description", ""))
                parts.append(exp.get("company", ""))

    education = profile.get("education") or []
    if isinstance(education, list):
        for edu in education:
            if isinstance(edu, dict):
                parts.append(edu.get("degree", ""))

    return " ".join(p for p in parts if p).strip()


def _build_vacancy_text(vacancy: dict[str, Any]) -> str:
    """Concatenate vacancy requirements and skills_required into a text string."""
    parts: list[str] = []

    parts.append(vacancy.get("title", ""))
    parts.append(vacancy.get("requirements", ""))
    parts.append(vacancy.get("description", ""))

    skills_required = vacancy.get("skills_required") or []
    if isinstance(skills_required, list):
        parts.append(" ".join(str(s) for s in skills_required))

    return " ".join(p for p in parts if p).strip()


def compute_match_score(
    jobseeker_profile: dict[str, Any],
    vacancy: dict[str, Any],
) -> float:
    """Compute cosine similarity between a jobseeker profile and a vacancy.

    Args:
        jobseeker_profile: Dict with keys ``skills``, ``experience``, ``education``.
        vacancy:           Dict with keys ``title``, ``requirements``,
                           ``description``, ``skills_required``.

    Returns:
        A float in the closed interval [0.0, 1.0].

    Requirements: 7.1
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    profile_text = _build_profile_text(jobseeker_profile)
    vacancy_text = _build_vacancy_text(vacancy)

    if not profile_text or not vacancy_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([profile_text, vacancy_text])
        score = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        # Clamp to [0.0, 1.0] to guard against floating-point edge cases
        return max(0.0, min(1.0, score))
    except Exception as exc:
        logger.error("compute_match_score failed: %s", exc, exc_info=True)
        return 0.0


def rank_vacancies(
    jobseeker_profile: dict[str, Any],
    vacancies: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Rank vacancies by match score for a given jobseeker profile.

    Attaches a ``match_score`` field to each vacancy dict and returns the
    list sorted in descending order of match score.

    Args:
        jobseeker_profile: Jobseeker profile dict.
        vacancies:         List of vacancy dicts.

    Returns:
        List of vacancy dicts with ``match_score`` field, sorted descending.

    Requirements: 7.1, 7.4
    """
    if not vacancies:
        return []

    profile_text = _build_profile_text(jobseeker_profile)

    if not profile_text:
        # No profile text — return vacancies with score 0 in original order
        for v in vacancies:
            v["match_score"] = 0.0
        return vacancies

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vacancy_texts = [_build_vacancy_text(v) for v in vacancies]
        corpus = [profile_text] + vacancy_texts

        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(corpus)

        profile_vec = tfidf_matrix[0:1]
        vacancy_vecs = tfidf_matrix[1:]
        scores = cosine_similarity(profile_vec, vacancy_vecs)[0]

        for vacancy, score in zip(vacancies, scores):
            vacancy["match_score"] = round(max(0.0, min(1.0, float(score))), 4)

    except Exception as exc:
        logger.error("rank_vacancies failed: %s", exc, exc_info=True)
        for v in vacancies:
            v["match_score"] = 0.0

    return sorted(vacancies, key=lambda v: v.get("match_score", 0.0), reverse=True)


def rank_applicants(
    vacancy: dict[str, Any],
    applicants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Rank applicants by match score for a given vacancy.

    Each applicant dict should contain a ``profile`` key with the jobseeker
    profile dict, or top-level ``skills``/``experience`` keys.

    Args:
        vacancy:    Vacancy dict.
        applicants: List of applicant dicts (each with profile data).

    Returns:
        List of applicant dicts with ``match_score`` field, sorted descending.

    Requirements: 7.3
    """
    if not applicants:
        return []

    vacancy_text = _build_vacancy_text(vacancy)

    if not vacancy_text:
        for a in applicants:
            a["match_score"] = 0.0
        return applicants

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        applicant_texts = [
            _build_profile_text(a.get("profile") or a) for a in applicants
        ]
        corpus = [vacancy_text] + applicant_texts

        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(corpus)

        vacancy_vec = tfidf_matrix[0:1]
        applicant_vecs = tfidf_matrix[1:]
        scores = cosine_similarity(vacancy_vec, applicant_vecs)[0]

        for applicant, score in zip(applicants, scores):
            applicant["match_score"] = round(max(0.0, min(1.0, float(score))), 4)

    except Exception as exc:
        logger.error("rank_applicants failed: %s", exc, exc_info=True)
        for a in applicants:
            a["match_score"] = 0.0

    return sorted(applicants, key=lambda a: a.get("match_score", 0.0), reverse=True)
