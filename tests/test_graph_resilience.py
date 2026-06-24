import unittest

from newsletter.graph import (
    HISTORICAL_DATA_WARNING,
    RetryPolicy,
    run_newsletter_graph,
)


class GraphResilienceTests(unittest.TestCase):
    def test_transient_research_failure_retries_with_backoff_then_completes(self):
        calls = []
        delays = []

        def researcher(topic):
            calls.append(topic)
            if len(calls) < 3:
                raise RuntimeError("temporary api outage")
            return "fresh technical research"

        result = run_newsletter_graph(
            {"topic": "LLM orchestration"},
            researcher=researcher,
            retry_policy=RetryPolicy(retries=3, backoff_seconds=(1.0, 2.0, 3.0)),
            sleeper=delays.append,
        )

        self.assertEqual(calls, ["LLM orchestration"] * 3)
        self.assertEqual(delays, [1.0, 2.0])
        self.assertEqual(result["research_source"], "technical_research_api")
        self.assertEqual(result["research_attempts"], 3)
        self.assertEqual(result["technical_research"], "fresh technical research")
        self.assertEqual(result["final_output"], "fresh technical research")
        self.assertEqual(result["status"], "completed")

    def test_permanent_research_failure_falls_back_and_still_completes(self):
        calls = []
        delays = []
        fallback_calls = []

        def researcher(topic):
            calls.append(topic)
            raise RuntimeError("api quota exceeded")

        def internal_knowledge(topic, error):
            fallback_calls.append((topic, type(error).__name__, str(error)))
            return "internal model summary"

        result = run_newsletter_graph(
            {"topic": "agentic newsletters"},
            researcher=researcher,
            internal_knowledge_model=internal_knowledge,
            retry_policy=RetryPolicy(retries=3, backoff_seconds=(1.0, 2.0, 3.0)),
            sleeper=delays.append,
        )

        self.assertEqual(calls, ["agentic newsletters"] * 4)
        self.assertEqual(delays, [1.0, 2.0, 3.0])
        self.assertEqual(
            fallback_calls,
            [("agentic newsletters", "RuntimeError", "api quota exceeded")],
        )
        self.assertEqual(result["research_source"], "internal_knowledge")
        self.assertEqual(result["research_attempts"], 4)
        self.assertEqual(result["status"], "completed")
        self.assertIn(HISTORICAL_DATA_WARNING, result["warnings"])
        self.assertIn(HISTORICAL_DATA_WARNING, result["technical_research"])
        self.assertIn("internal model summary", result["technical_research"])
        self.assertIn(HISTORICAL_DATA_WARNING, result["final_output"])
        self.assertIn("internal model summary", result["final_output"])
        self.assertEqual(len(result["errors"]), 4)


if __name__ == "__main__":
    unittest.main()
