import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class PhaseTimer:
    phase_id: str
    start_time_ns: int = field(default_factory=time.perf_counter_ns)
    end_time_ns: int | None = None

    def stop(self) -> int:
        self.end_time_ns = time.perf_counter_ns()
        return self.duration_ms

    @property
    def duration_ms(self) -> int:
        if self.end_time_ns is None:
            raise ValueError(f"Timer {self.phase_id} not stopped")
        return (self.end_time_ns - self.start_time_ns) // 1_000_000


@dataclass
class PerformanceMetrics:
    phase_timings: dict[str, int] = field(default_factory=dict)
    total_duration_ms: int = 0

    def record_phase(self, phase_id: str, duration_ms: int) -> None:
        self.phase_timings[phase_id] = duration_ms

    def finalize(self) -> None:
        self.total_duration_ms = sum(self.phase_timings.values())

    def to_dict(self) -> dict:
        return {"total_duration_ms": self.total_duration_ms, "phase_breakdown": self.phase_timings}


@contextmanager
def timed_phase(metrics: PerformanceMetrics, phase_id: str):
    timer = PhaseTimer(phase_id=phase_id)
    try:
        yield timer
    finally:
        duration = timer.stop()
        metrics.record_phase(phase_id, duration)
