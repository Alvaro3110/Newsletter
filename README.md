# Newsletter

Backend helper modules for the Newsletter project.

## Telemetry

`newsletter.telemetry.TelemetryRun` records token usage for graph nodes during an
edit execution and writes `telemetry.json` into the edition folder when finalized.

```python
from newsletter.telemetry import ModelPricing, TelemetryRun

pricing = {
    "gpt-test": ModelPricing(
        input_usd_per_million_tokens=2,
        output_usd_per_million_tokens=8,
    )
}

with TelemetryRun("editions/edition-001", pricing) as telemetry:
    telemetry.record_node(
        "draft",
        "gpt-test",
        input_tokens=1000,
        output_tokens=500,
    )
```

The generated JSON includes:

- `total_tokens`: sum of all recorded graph node tokens.
- `cost_usd`: model-based token cost in USD.
- `duration_seconds`: total execution duration for the run.
