"""Structured telemetry writer for backend edit executions."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from time import monotonic
from typing import Any, Callable, Iterable, Mapping

TELEMETRY_FILENAME = "telemetry.json"
_MILLION = Decimal("1000000")
_COST_QUANT = Decimal("0.00000001")
_DURATION_QUANT = Decimal("0.000001")


@dataclass(frozen=True)
class ModelPricing:
    """Per-model pricing expressed in USD per million tokens."""

    input_usd_per_million_tokens: Decimal | float | int | str
    output_usd_per_million_tokens: Decimal | float | int | str
    total_usd_per_million_tokens: Decimal | float | int | str | None = None

    def input_price(self) -> Decimal:
        return _as_decimal(self.input_usd_per_million_tokens)

    def output_price(self) -> Decimal:
        return _as_decimal(self.output_usd_per_million_tokens)

    def total_price(self) -> Decimal | None:
        if self.total_usd_per_million_tokens is None:
            return None
        return _as_decimal(self.total_usd_per_million_tokens)

    def cost_for(self, usage: "GraphNodeUsage") -> Decimal:
        if usage.has_input_output_breakdown:
            input_cost = Decimal(usage.input_tokens) * self.input_price()
            output_cost = Decimal(usage.output_tokens) * self.output_price()
            return (input_cost + output_cost) / _MILLION

        total_price = self.total_price()
        if total_price is None:
            raise ValueError(
                "total token pricing is required when node usage has no input/output breakdown"
            )
        return Decimal(usage.total_tokens) * total_price / _MILLION


@dataclass(frozen=True)
class GraphNodeUsage:
    """Token usage emitted by one node in the edit graph."""

    node_name: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens_override: int | None = None

    def __post_init__(self) -> None:
        if not self.node_name:
            raise ValueError("node_name is required")
        if not self.model:
            raise ValueError("model is required")
        _validate_token_count("input_tokens", self.input_tokens)
        _validate_token_count("output_tokens", self.output_tokens)
        if self.total_tokens_override is not None:
            _validate_token_count("total_tokens", self.total_tokens_override)

    @property
    def has_input_output_breakdown(self) -> bool:
        return self.input_tokens > 0 or self.output_tokens > 0

    @property
    def total_tokens(self) -> int:
        if self.total_tokens_override is not None:
            return self.total_tokens_override
        return self.input_tokens + self.output_tokens

    def to_json(self, pricing: ModelPricing) -> dict[str, Any]:
        return {
            "node_name": self.node_name,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": _decimal_to_float(pricing.cost_for(self), _COST_QUANT),
        }


class TelemetryRun:
    """Collect graph node usage and write telemetry after an edit execution."""

    def __init__(
        self,
        edition_dir: str | Path,
        model_pricing: Mapping[str, ModelPricing],
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.edition_dir = Path(edition_dir)
        self.model_pricing = dict(model_pricing)
        self._clock = clock
        self._started_at = self._clock()
        self._nodes: list[GraphNodeUsage] = []
        self._finalized = False

    def __enter__(self) -> "TelemetryRun":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        self.finalize()
        return False

    def record_node(
        self,
        node_name: str,
        model: str,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int | None = None,
    ) -> GraphNodeUsage:
        usage = GraphNodeUsage(
            node_name=node_name,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens_override=total_tokens,
        )
        self._nodes.append(usage)
        return usage

    def payload(self) -> dict[str, Any]:
        duration_seconds = max(0.0, self._clock() - self._started_at)
        return build_telemetry_payload(
            self._nodes,
            self.model_pricing,
            duration_seconds=duration_seconds,
        )

    def finalize(self) -> Path:
        payload = self.payload()
        path = self.edition_dir / TELEMETRY_FILENAME
        self.edition_dir.mkdir(parents=True, exist_ok=True)
        _write_json_atomic(path, payload)
        self._finalized = True
        return path

    @property
    def finalized(self) -> bool:
        return self._finalized


def build_telemetry_payload(
    graph_nodes: Iterable[GraphNodeUsage | Mapping[str, Any]],
    model_pricing: Mapping[str, ModelPricing],
    *,
    duration_seconds: float,
) -> dict[str, Any]:
    """Build the structured telemetry JSON payload for one edit execution."""

    nodes = [_coerce_node_usage(node) for node in graph_nodes]
    total_tokens = sum(node.total_tokens for node in nodes)
    total_cost = Decimal("0")
    serialized_nodes: list[dict[str, Any]] = []

    for node in nodes:
        try:
            pricing = model_pricing[node.model]
        except KeyError as exc:
            raise KeyError(f"missing pricing for model {node.model!r}") from exc

        total_cost += pricing.cost_for(node)
        serialized_nodes.append(node.to_json(pricing))

    return {
        "total_tokens": total_tokens,
        "cost_usd": _decimal_to_float(total_cost, _COST_QUANT),
        "duration_seconds": _decimal_to_float(
            Decimal(str(max(0.0, duration_seconds))),
            _DURATION_QUANT,
        ),
        "nodes": serialized_nodes,
    }


def _coerce_node_usage(node: GraphNodeUsage | Mapping[str, Any]) -> GraphNodeUsage:
    if isinstance(node, GraphNodeUsage):
        return node

    total_tokens = node.get("total_tokens")
    return GraphNodeUsage(
        node_name=str(node["node_name"]),
        model=str(node["model"]),
        input_tokens=int(node.get("input_tokens", 0)),
        output_tokens=int(node.get("output_tokens", 0)),
        total_tokens_override=None if total_tokens is None else int(total_tokens),
    )


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    tmp_path = path.with_name(f".{path.name}.tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp_path, path)


def _as_decimal(value: Decimal | float | int | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _decimal_to_float(value: Decimal, quant: Decimal) -> float:
    return float(value.quantize(quant, rounding=ROUND_HALF_UP))


def _validate_token_count(name: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
