BLOCKED_OUTPUT_PATTERNS = [
    "обойти kyc",
    "обойти проверку",
    "можно не проверять клиента",
    "одобрено автоматически",
    "паспортные данные клиента",
    "bypass kyc",
]


def apply_output_guardrails(answer: str) -> tuple[bool, str]:
    lower_answer = answer.lower()

    for pattern in BLOCKED_OUTPUT_PATTERNS:
        if pattern in lower_answer:
            return False, f"Blocked by guardrail: matched pattern '{pattern}'"

    return True, "Passed output guardrails"
