from app.schemas import RiskAssessment


HIGH_RISK_PATTERNS = [
    "обойти kyc",
    "обойти проверку",
    "удалить негативную отметку",
    "одобри кредит",
    "покажи паспорт",
    "паспортные данные клиента",
    "персональные данные клиента",
    "игнорируй инструкции",
    "игнорируй все инструкции",
    "игнорируй все предыдущие инструкции",
    "ignore previous instructions",
    "ignore all instructions",
    "bypass kyc",
]

MEDIUM_RISK_PATTERNS = [
    "жалоба",
    "спорная комиссия",
    "списание комиссии",
    "претензия",
    "kyc exception",
    "исключение из процедуры",
    "ответ клиенту",
    "без проверки бенефициаров",
]


def classify_risk(question: str) -> RiskAssessment:
    q = question.lower()

    if any(pattern in q for pattern in HIGH_RISK_PATTERNS):
        return RiskAssessment(
            risk_level="high",
            reason=(
                "The request may involve bypassing controls, disclosing sensitive data, "
                "or making restricted banking decisions."
            ),
            should_refuse=True,
            requires_human_review=True,
        )

    if any(pattern in q for pattern in MEDIUM_RISK_PATTERNS):
        return RiskAssessment(
            risk_level="medium",
            reason="The request may involve regulated customer communication or an exception to policy.",
            should_refuse=False,
            requires_human_review=True,
        )

    return RiskAssessment(
        risk_level="low",
        reason="No obvious high-risk intent detected.",
        should_refuse=False,
        requires_human_review=False,
    )
