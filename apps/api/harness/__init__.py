"""Agent harness — breaker + step envelope + guarded chat.

One import point for pipeline code. `guarded_chat_call` routes every LLM
completion through the shared circuit breaker so an upstream outage fails
fast across the whole app instead of per-step retry storms.
"""

from harness.breaker import CHAT_BREAKER, BreakerOpen, CircuitBreaker
from harness.steps import (
    StepResult,
    current_run_id,
    new_run_id,
    set_run_id,
    step,
    step_required,
)


def guarded_chat_call(chat, method: str, *args, **kwargs):
    """Call chat.<method> through the circuit breaker.

    Raises BreakerOpen when the upstream is known-bad; callers fall back to
    templates (existing behavior) instead of burning retries.
    """
    return CHAT_BREAKER.call(getattr(chat, method), *args, **kwargs)
