"""Offline SEC-05 reference fixture for one runtime authorization boundary.

The caller identity is supplied by the harness, separately from the requested
operation. This fixture exercises authorization and state mutation in memory.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Outcome:
    control: str
    decision: str
    before: int
    after: int


class CounterBoundary:
    """Only the synthetic operator may increment the in-memory counter."""

    def __init__(self):
        self._counter = 0

    @property
    def counter(self):
        return self._counter

    def authorize(self, caller: str, operation: str) -> bool:
        return caller == "operator" and operation == "increment"

    def execute(self, caller: str, operation: str) -> bool:
        if not self.authorize(caller, operation):
            return False
        if operation != "increment":
            raise ValueError(f"Unknown fixture operation: {operation}")
        self._counter += 1
        return True


def run_controls(boundary: CounterBoundary) -> tuple[Outcome, ...]:
    outcomes = []
    for control, caller in (("unauthorized", "observer"), ("authorized", "operator")):
        before = boundary.counter
        allowed = boundary.execute(caller, "increment")
        outcomes.append(Outcome(control, "allowed" if allowed else "denied", before, boundary.counter))
    return tuple(outcomes)


def verify_controls(outcomes: tuple[Outcome, ...]) -> None:
    expected = (
        Outcome("unauthorized", "denied", 0, 0),
        Outcome("authorized", "allowed", 0, 1),
    )
    if outcomes != expected:
        raise ValueError(f"Runtime controls failed: observed {outcomes!r}")


if __name__ == "__main__":
    observed = run_controls(CounterBoundary())
    print(json.dumps([asdict(outcome) for outcome in observed], indent=2))
    verify_controls(observed)
