def build_human_review_payload(
    question: str,
    reason: str,
    draft_answer: str | None = None,
) -> dict:
    return {
        "status": "needs_human_review",
        "reason": reason,
        "suggested_reviewer": "compliance_or_operations_specialist",
        "question": question,
        "draft_answer": draft_answer,
    }
