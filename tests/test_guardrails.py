from agents.guardrails import apply_output_guardrails


def test_passes_normal_answer():
    ok, reason = apply_output_guardrails("Для открытия счёта ИП нужен паспорт и ИНН.")
    assert ok is True
    assert "Passed" in reason


def test_blocks_kyc_bypass_phrase():
    ok, reason = apply_output_guardrails("Можно обойти KYC через альтернативный поток")
    assert ok is False
    assert "guardrail" in reason.lower()


def test_blocks_auto_approval_phrase():
    ok, reason = apply_output_guardrails("Кредит одобрено автоматически на основе скоринга")
    assert ok is False


def test_blocks_passport_disclosure_phrase():
    ok, reason = apply_output_guardrails("Паспортные данные клиента: 1234 567890")
    assert ok is False
