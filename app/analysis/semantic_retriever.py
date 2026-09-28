"""
Hybrid Semantic & Lexical Retriever for iSync.
Combines exact terminology detection, stem overlap, TF-IDF cosine similarity,
and hierarchical context scoring to discover candidate course chunks.
Distinguishes Direct Match, Semantic Match, and Possible Impact.
"""

import re
from typing import List, Tuple
from pydantic import BaseModel
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.schemas import SoftwareChange, ContentChunk, ChangeType


class RetrievedCandidate(BaseModel):
    change: SoftwareChange
    chunk: ContentChunk
    match_type: str  # "DIRECT MATCH", "SEMANTIC MATCH", "POSSIBLE IMPACT"
    score: float
    reasons: List[str]


class SemanticRetriever:
    """Retrieves course content chunks matching a software change using hybrid techniques."""

    def __init__(self, threshold: float = 0.25):
        self.threshold = threshold

    def retrieve_candidates(
        self,
        change: SoftwareChange,
        chunks: List[ContentChunk],
    ) -> List[RetrievedCandidate]:
        if not chunks:
            return []

        # Build corpus texts
        corpus = [f"{c.text} {c.heading or ''} {c.section or ''} {c.lesson or ''}" for c in chunks]
        query = f"{change.title} {change.description} {change.affected_subsystem} {' '.join(change.keywords)}"
        if change.old_term:
            query += f" {change.old_term}"

        # TF-IDF cosine similarity
        try:
            vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            mat = vec.fit_transform(corpus)
            q_vec = vec.transform([query])
            sem_scores = cosine_similarity(q_vec, mat).flatten()
        except Exception:
            sem_scores = np.zeros(len(chunks))

        candidates: List[RetrievedCandidate] = []

        for idx, chunk in enumerate(chunks):
            text_lower = chunk.text.lower()
            context_lower = f"{chunk.exact_location} {chunk.heading or ''}".lower()
            sem_score = float(sem_scores[idx])

            lexical_hits = 0
            reasons = []

            # 1. Check exact old terminology or feature title
            has_direct_term = False
            if change.old_term and change.old_term.lower() in text_lower:
                has_direct_term = True
                reasons.append(f"Direct match on obsolete terminology: '{change.old_term}'")

            # Check primary feature name
            feature_primary = change.keywords[0].lower() if change.keywords else ""
            if feature_primary and feature_primary in text_lower:
                lexical_hits += 2
                reasons.append(f"Direct match on feature keyword: '{feature_primary}'")

            # 2. Check stem / keyword overlap
            for kw in change.keywords:
                kw_low = kw.lower()
                stem = kw_low.rstrip("s")
                if kw_low in text_lower or (len(stem) > 3 and stem in text_lower):
                    lexical_hits += 1

            lex_ratio = min(lexical_hits / max(len(change.keywords), 1), 1.0)

            # 3. Contextual subsystem alignment
            ctx_score = 0.0
            subsystems = re.split(r"[/&,]", change.affected_subsystem.lower())
            for s in subsystems:
                s_clean = s.strip().rstrip("s")
                if len(s_clean) > 3 and s_clean in context_lower:
                    ctx_score += 0.5
                    break

            # 4. Screenshot / UI alignment
            if change.change_type == ChangeType.UI_CHANGE and chunk.has_image_or_screenshot:
                if any(k.lower() in text_lower for k in change.keywords[:4]):
                    ctx_score += 0.4
                    reasons.append("Visual diagram/screenshot corresponding to redesigned UI")

            # Calculate combined score
            combined = (0.35 * lex_ratio) + (0.45 * sem_score) + (0.20 * ctx_score)

            # Direct Terminology override
            if has_direct_term:
                combined = max(combined, 0.88)

            if combined < self.threshold:
                continue

            # Classify match type
            if has_direct_term or (lex_ratio >= 0.5 and sem_score >= 0.4):
                match_type = "DIRECT MATCH"
            elif combined >= 0.40 or sem_score >= 0.35:
                match_type = "SEMANTIC MATCH"
            else:
                match_type = "POSSIBLE IMPACT"

            candidates.append(
                RetrievedCandidate(
                    change=change,
                    chunk=chunk,
                    match_type=match_type,
                    score=round(combined, 3),
                    reasons=reasons,
                )
            )

        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates
