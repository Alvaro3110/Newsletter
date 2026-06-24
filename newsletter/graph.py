"""LangGraph-style nodes for resilient newsletter research."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any

HISTORICAL_DATA_WARNING = (
    "Aviso de dados historicos: a pesquisa tecnica externa falhou; "
    "este trecho foi produzido com conhecimento interno do modelo e pode estar desatualizado."
)

ResearchState = MutableMapping[str, Any]
StateInput = Mapping[str, Any]
Researcher = Callable[[str], str]
InternalKnowledgeModel = Callable[[str, Exception], str]
Sleeper = Callable[[float], None]


@dataclass(frozen=True)
class RetryPolicy:
    """Retry configuration for the technical research node."""

    retries: int = 3
    backoff_seconds: tuple[float, ...] = (0.25, 0.5, 1.0)

    def __post_init__(self) -> None:
        if self.retries < 0:
            raise ValueError("retries must be greater than or equal to zero")
        if len(self.backoff_seconds) < self.retries:
            raise ValueError("backoff_seconds must contain one delay per retry")
        if any(delay < 0 for delay in self.backoff_seconds):
            raise ValueError("backoff_seconds cannot contain negative delays")

    @property
    def max_attempts(self) -> int:
        return self.retries + 1

    def delay_before_retry(self, retry_index: int) -> float:
        """Return the delay before retry number 1..retries."""

        if retry_index < 1 or retry_index > self.retries:
            raise ValueError("retry_index must be between 1 and retries")
        return self.backoff_seconds[retry_index - 1]


def default_internal_knowledge_model(topic: str, error: Exception) -> str:
    """Fallback text used when a real model callable is not injected."""

    return (
        f"Resumo historico sobre {topic}: nao foi possivel consultar a pesquisa "
        f"tecnica em tempo real. Ultimo erro observado: {type(error).__name__}."
    )


def technical_research_node(
    state: StateInput,
    *,
    researcher: Researcher,
    internal_knowledge_model: InternalKnowledgeModel = default_internal_knowledge_model,
    retry_policy: RetryPolicy = RetryPolicy(),
    sleeper: Sleeper = time.sleep,
) -> ResearchState:
    """Run technical research with retries and an internal-knowledge fallback.

    The node treats the input and output as a LangGraph state dictionary: it
    copies the incoming state, adds research metadata, and never mutates the
    caller-owned mapping in place.
    """

    topic = _required_topic(state)
    next_state = _copy_state(state)
    errors = list(next_state.get("errors", []))

    for attempt in range(1, retry_policy.max_attempts + 1):
        try:
            research = researcher(topic)
        except Exception as exc:  # noqa: PERF203 - each attempt needs its own error.
            errors.append(f"technical research attempt {attempt} failed: {exc}")
            next_state["errors"] = errors

            if attempt <= retry_policy.retries:
                sleeper(retry_policy.delay_before_retry(attempt))
                continue

            fallback = internal_knowledge_model(topic, exc)
            warnings = list(next_state.get("warnings", []))
            warnings.append(HISTORICAL_DATA_WARNING)

            next_state.update(
                {
                    "technical_research": f"{HISTORICAL_DATA_WARNING}\n\n{fallback}",
                    "research_source": "internal_knowledge",
                    "research_attempts": attempt,
                    "warnings": warnings,
                    "status": "research_fallback",
                }
            )
            return next_state

        next_state.update(
            {
                "technical_research": research,
                "research_source": "technical_research_api",
                "research_attempts": attempt,
                "errors": errors,
                "status": "research_complete",
            }
        )
        return next_state

    raise RuntimeError("unreachable retry loop exit")


def final_response_node(state: StateInput) -> ResearchState:
    """Produce a final completed graph state from the research state."""

    technical_research = state.get("technical_research")
    if not technical_research:
        raise ValueError("technical_research is required before final response")

    next_state = _copy_state(state)
    warnings = list(next_state.get("warnings", []))
    warning_block = "\n".join(warnings)
    final_output = str(technical_research)
    if warning_block and not final_output.startswith(warning_block):
        final_output = f"{warning_block}\n\n{final_output}"

    next_state.update(
        {
            "final_output": final_output,
            "status": "completed",
        }
    )
    return next_state


def run_newsletter_graph(
    state: StateInput,
    *,
    researcher: Researcher,
    internal_knowledge_model: InternalKnowledgeModel = default_internal_knowledge_model,
    retry_policy: RetryPolicy = RetryPolicy(),
    sleeper: Sleeper = time.sleep,
) -> ResearchState:
    """Execute the current newsletter graph path end to end."""

    researched_state = technical_research_node(
        state,
        researcher=researcher,
        internal_knowledge_model=internal_knowledge_model,
        retry_policy=retry_policy,
        sleeper=sleeper,
    )
    return final_response_node(researched_state)


def _required_topic(state: StateInput) -> str:
    topic = str(state.get("topic", "")).strip()
    if not topic:
        raise ValueError("state['topic'] is required")
    return topic


def _copy_state(state: StateInput) -> ResearchState:
    return dict(state)
