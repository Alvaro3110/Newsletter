import json
import shutil
import tempfile
import unittest
from pathlib import Path

from newsletter.telemetry import (
    TELEMETRY_FILENAME,
    GraphNodeUsage,
    ModelPricing,
    TelemetryRun,
    build_telemetry_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_TMP_ROOT = REPO_ROOT / ".tmp-test-runs"


class FakeClock:
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class TelemetryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        LOCAL_TMP_ROOT.mkdir(exist_ok=True)
        self.temp_dir = tempfile.TemporaryDirectory(dir=LOCAL_TMP_ROOT)
        self.addCleanup(self._remove_local_tmp_root_if_empty)
        self.addCleanup(self.temp_dir.cleanup)

    def test_context_manager_writes_telemetry_json_in_edition_dir(self) -> None:
        clock = FakeClock(10.0)
        pricing = {"gpt-test": ModelPricing(2, 8)}
        edition_dir = Path(self.temp_dir.name) / "edition-001"

        with TelemetryRun(edition_dir, pricing, clock=clock) as telemetry:
            telemetry.record_node(
                "draft",
                "gpt-test",
                input_tokens=1_000,
                output_tokens=500,
            )
            clock.advance(2.5)

        telemetry_path = edition_dir / TELEMETRY_FILENAME
        self.assertTrue(telemetry_path.exists())

        payload = json.loads(telemetry_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["total_tokens"], 1_500)
        self.assertEqual(payload["cost_usd"], 0.006)
        self.assertEqual(payload["duration_seconds"], 2.5)

    def test_payload_sums_all_graph_nodes_and_model_costs(self) -> None:
        payload = build_telemetry_payload(
            [
                GraphNodeUsage(
                    "outline",
                    "gpt-test",
                    input_tokens=1_000,
                    output_tokens=250,
                ),
                {
                    "node_name": "review",
                    "model": "fast-total",
                    "total_tokens": 2_000,
                },
            ],
            {
                "gpt-test": ModelPricing(2, 8),
                "fast-total": ModelPricing(0, 0, total_usd_per_million_tokens=5),
            },
            duration_seconds=3.75,
        )

        self.assertEqual(payload["total_tokens"], 3_250)
        self.assertEqual(payload["cost_usd"], 0.014)
        self.assertEqual(payload["duration_seconds"], 3.75)
        self.assertEqual(len(payload["nodes"]), 2)

    def test_missing_model_pricing_is_rejected(self) -> None:
        with self.assertRaisesRegex(KeyError, "missing pricing"):
            build_telemetry_payload(
                [GraphNodeUsage("draft", "unknown-model", input_tokens=1)],
                {},
                duration_seconds=0.1,
            )

    def test_token_counts_must_be_non_negative(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-negative"):
            GraphNodeUsage("draft", "gpt-test", input_tokens=-1)

    def _remove_local_tmp_root_if_empty(self) -> None:
        try:
            LOCAL_TMP_ROOT.rmdir()
        except OSError:
            pass


if __name__ == "__main__":
    unittest.main()
