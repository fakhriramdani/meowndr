"""
Candidate Selector & Asset Provenance Tracker for @meowndr Papercraft Explainer.
Compares multi-pass generated candidates, selects the optimal illustration based on QA score,
and persists complete prompt and generation audit trails.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from .illustration_qa import IllustrationQAReport


@dataclass
class IllustrationCandidate:
    candidate_id: str
    image_path: str
    prompt_used: str
    qa_report: IllustrationQAReport
    created_at: str
    is_selected: bool = False


class CandidateSelector:
    """Ranks and selects the highest-quality candidate among multi-pass generations."""

    @classmethod
    def select_best_candidate(cls, candidates: List[IllustrationCandidate]) -> Optional[IllustrationCandidate]:
        if not candidates:
            return None

        # Sort primarily by verdict ("APPROVED" before "NEEDS_REVIEW" before "RETRY_REQUIRED")
        # and secondarily by overall QA score
        def candidate_rank_key(c: IllustrationCandidate):
            verdict_weight = 3 if c.qa_report.verdict == "APPROVED" else (1 if c.qa_report.verdict == "NEEDS_REVIEW" else 0)
            return (verdict_weight, c.qa_report.overall_score)

        sorted_candidates = sorted(candidates, key=candidate_rank_key, reverse=True)
        winner = sorted_candidates[0]
        winner.is_selected = True

        for c in sorted_candidates[1:]:
            c.is_selected = False

        return winner

    @classmethod
    def compile_selection_metadata(cls, scene_id: str, candidates: List[IllustrationCandidate]) -> Dict[str, Any]:
        winner = cls.select_best_candidate(candidates)
        return {
            "scene_id": scene_id,
            "total_candidates": len(candidates),
            "selected_candidate_id": winner.candidate_id if winner else None,
            "selected_image_path": winner.image_path if winner else None,
            "selected_overall_score": winner.qa_report.overall_score if winner else 0.0,
            "selected_verdict": winner.qa_report.verdict if winner else "NONE",
            "candidates_audit": [
                {
                    "candidate_id": c.candidate_id,
                    "image_path": c.image_path,
                    "overall_score": c.qa_report.overall_score,
                    "verdict": c.qa_report.verdict,
                    "attempt": c.qa_report.attempt,
                    "is_selected": c.is_selected,
                    "detected_flaws": c.qa_report.detected_flaws
                }
                for c in candidates
            ]
        }
