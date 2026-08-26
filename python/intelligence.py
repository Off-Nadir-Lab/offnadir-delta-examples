"""AI assessment and the analyst agent (metered — these are the expensive calls)."""

from offnadir_delta import Client
from offnadir_delta.errors import InsufficientTokensError, PermissionDeniedError

AOI = [22.0, 44.0, 40.0, 53.0]


def main() -> None:
    with Client() as client:
        if not client.usage().plan.api_llm_access:
            print("This key's plan does not have LLM access (Pro required). Skipping.")
            return

        try:
            # Assess the single highest-severity recent signal.
            page = client.signals.list(bbox=AOI, days=7, sort="severity", limit=1)
            if page.signals and page.signals[0].id is not None:
                event_id = page.signals[0].id
                assessment = client.intelligence.assess(event_id, kind="quick")
                print("Assessment:\n", assessment.content, "\n")

            # Free-form analyst question (metered 5-123 tokens, not idempotent).
            answer = client.intelligence.analyst(
                "What is the most significant escalation this week and why?",
                bbox=AOI,
            )
            print("Analyst brief:\n", answer.brief)
        except PermissionDeniedError:
            print("Pro plan required for these endpoints.")
        except InsufficientTokensError as e:
            print(f"Not enough tokens (need {e.required}, have {e.available}).")


if __name__ == "__main__":
    main()
