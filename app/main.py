from fastapi import FastAPI

from agents.answer_agent import generate_answer
from agents.escalation_agent import build_human_review_payload
from agents.guardrails import apply_output_guardrails
from agents.judge_agent import judge_answer
from agents.retriever_agent import retrieve_context
from agents.risk_classifier import classify_risk
from app.schemas import AgentRequest, AgentResponse
from utils.audit import write_audit_log


app = FastAPI(title="Bank Policy RAG Copilot")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/ask", response_model=AgentResponse)
def ask_agent(request: AgentRequest) -> AgentResponse:
    risk = classify_risk(request.question)

    if risk.should_refuse:
        response = AgentResponse(
            status="refused",
            answer=(
                "Я не могу помочь с обходом банковских процедур, раскрытием персональных данных "
                "или автономным принятием регулируемых решений. Вопрос передан на ручную проверку."
            ),
            risk=risk,
            sources=[],
            judge_score=None,
        )
        write_audit_log(request, response)
        return response

    sources = retrieve_context(request.question)

    if not sources:
        response = AgentResponse(
            status="needs_human_review",
            answer="Я не нашёл подтверждения в утверждённых документах. Вопрос требует ручной проверки.",
            risk=risk,
            sources=[],
            judge_score=None,
        )
        write_audit_log(request, response)
        return response

    answer = generate_answer(request.question, sources)

    passed, guardrail_reason = apply_output_guardrails(answer)
    if not passed:
        response = AgentResponse(
            status="needs_human_review",
            answer=f"Ответ заблокирован guardrails. Причина: {guardrail_reason}",
            risk=risk,
            sources=sources,
            judge_score=None,
        )
        write_audit_log(request, response)
        return response

    judge_score = judge_answer(request.question, answer, sources)

    needs_review = (
        risk.requires_human_review
        or bool(judge_score.get("requires_human_review"))
        or not bool(judge_score.get("pass"))
    )

    if needs_review:
        review_payload = build_human_review_payload(
            question=request.question,
            reason=risk.reason,
            draft_answer=answer,
        )
        response = AgentResponse(
            status="needs_human_review",
            answer=f"Draft prepared for human review:\n\n{answer}",
            risk=risk,
            sources=sources,
            judge_score=judge_score,
        )
        write_audit_log(request, response, extra=review_payload)
        return response

    response = AgentResponse(
        status="answered",
        answer=answer,
        risk=risk,
        sources=sources,
        judge_score=judge_score,
    )
    write_audit_log(request, response)
    return response
