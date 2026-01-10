"""Chunk Processor with Exponential Backoff - Consolidated Implementation.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Chunk Processor
PHASE_ROLE: Process document chunks with retry and error handling

Consolidated Implementation:
Uses the shared retry utility in src/farfan_pipeline/utils/retry.py
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 2
__stage__ = 50
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"



from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from farfan_pipeline.utils.retry import (
    PermanentError,
    RetryConfig,
    RetryPolicy,
    TransientError,
    with_exponential_backoff,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


# === EXCEPTIONS ===


class ChunkProcessingError(Exception):
    """Raised when chunk processing fails after all retries."""

    def __init__(self, chunk_id: str, attempts: int, last_error: str):
        self.chunk_id = chunk_id
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"Chunk {chunk_id} failed after {attempts} attempts: {last_error}")


# === DATA MODELS ===


@dataclass
class Chunk:
    """A document chunk to process.

    Attributes:
        chunk_id: Unique identifier
        content: Chunk text content
        metadata: Additional metadata
    """

    chunk_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkResult:
    """Result of processing a chunk.

    Attributes:
        chunk_id: Identifier of processed chunk
        success: Whether processing succeeded
        output: Processing output (if successful)
        error: Error message (if failed)
        attempts: Number of attempts made
        total_time_ms: Total processing time including retries
    """

    chunk_id: str
    success: bool
    output: Any = None
    error: str | None = None
    attempts: int = 1
    total_time_ms: float = 0.0


# === CHUNK PROCESSOR ===


class RetryableChunkProcessor:
    """
    Processes chunks with exponential backoff retry.
    Uses shared RetryPolicy for consistent behavior and metrics.
    """

    def __init__(self, processor_func: Callable[[Chunk], Any], config: RetryConfig | None = None):
        """
        Initialize chunk processor.

        Args:
            processor_func: Function to process each chunk.
            config: Retry configuration.
        """
        self.processor_func = processor_func
        self.config = config or RetryConfig()
        self.policy = RetryPolicy(config=self.config)

    def process_chunk(self, chunk: Chunk) -> ChunkResult:
        """
        Process a single chunk with retry logic.
        """
        start_time = time.perf_counter()
        attempts = 0
        last_error = None

        for attempt in self.policy.attempts():
            attempts = attempt.attempt_num + 1
            try:
                output = self.processor_func(chunk)
                attempt.mark_success()

                total_time_ms = (time.perf_counter() - start_time) * 1000
                return ChunkResult(
                    chunk_id=chunk.chunk_id,
                    success=True,
                    output=output,
                    attempts=attempts,
                    total_time_ms=total_time_ms,
                )
            except Exception as e:
                last_error = str(e)
                try:
                    attempt.retry_on(e)
                except Exception:
                    # Retry limit exceeded or permanent error
                    break

        total_time_ms = (time.perf_counter() - start_time) * 1000
        return ChunkResult(
            chunk_id=chunk.chunk_id,
            success=False,
            error=last_error,
            attempts=attempts,
            total_time_ms=total_time_ms,
        )

    def process_chunks(self, chunks: list[Chunk]) -> list[ChunkResult]:
        """Process multiple chunks."""
        results = [self.process_chunk(chunk) for chunk in chunks]
        successful = sum(1 for r in results if r.success)
        logger.info(
            f"Processed {len(chunks)} chunks: {successful} succeeded, {len(chunks) - successful} failed"
        )
        return results

    def get_metrics(self) -> dict[str, Any]:
        """Get processing metrics from shared config."""
        return self.config.get_metrics()


# === ASYNC CHUNK PROCESSOR ===


class AsyncRetryableChunkProcessor:
    """
    Async version of chunk processor with exponential backoff.
    Currently uses with_exponential_backoff decorator on an internal method.
    """

    def __init__(self, processor_func: Callable[[Chunk], Any], config: RetryConfig | None = None):
        self.processor_func = processor_func
        self.config = config or RetryConfig()

    async def process_chunk(self, chunk: Chunk) -> ChunkResult:
        """Process a single chunk asynchronously with retry."""
        import asyncio

        start_time = time.perf_counter()
        attempts = 0
        last_error = None

        # Manual retry loop for async support since current with_exponential_backoff is sync
        for attempt_num in range(self.config.max_retries + 1):
            attempts = attempt_num + 1
            self.config.total_chunks += 1
            try:
                output = await self.processor_func(chunk)
                self.config.successful_chunks += 1
                total_time_ms = (time.perf_counter() - start_time) * 1000
                self.config.total_time_ms += total_time_ms
                return ChunkResult(
                    chunk_id=chunk.chunk_id,
                    success=True,
                    output=output,
                    attempts=attempts,
                    total_time_ms=total_time_ms,
                )
            except Exception as e:
                last_error = str(e)
                if isinstance(e, PermanentError) or attempt_num >= self.config.max_retries:
                    self.config.failed_chunks += 1
                    break

                self.config.total_retries += 1
                delay = min(
                    self.config.base_delay_seconds * (self.config.multiplier**attempt_num),
                    self.config.max_delay_seconds,
                )
                import random

                delay += delay * self.config.jitter_factor * random.random()

                if self.config.on_retry:
                    self.config.on_retry(e, attempts, delay * 1000)

                await asyncio.sleep(delay)

        total_time_ms = (time.perf_counter() - start_time) * 1000
        self.config.total_time_ms += total_time_ms
        return ChunkResult(
            chunk_id=chunk.chunk_id,
            success=False,
            error=last_error,
            attempts=attempts,
            total_time_ms=total_time_ms,
        )

    async def process_chunks(self, chunks: list[Chunk]) -> list[ChunkResult]:
        """Process multiple chunks concurrently."""
        import asyncio

        tasks = [self.process_chunk(chunk) for chunk in chunks]
        return await asyncio.gather(*tasks)

    def get_metrics(self) -> dict[str, Any]:
        """Get processing metrics."""
        return self.config.get_metrics()


# === CONVENIENCE FUNCTIONS ===


def process_with_retry(func: Callable[[], T], max_retries: int = 4, base_delay: float = 1.0) -> T:
    """Execute a function with exponential backoff retry using shared utility."""
    config = RetryConfig(max_retries=max_retries, base_delay_seconds=base_delay)

    @with_exponential_backoff(config=config)
    def wrapped():
        return func()

    return wrapped()


# === MODULE EXPORTS ===

__all__ = [
    # Exceptions
    "TransientError",
    "PermanentError",
    "ChunkProcessingError",
    # Data models
    "Chunk",
    "ChunkResult",
    "RetryConfig",
    # Processors
    "RetryableChunkProcessor",
    "AsyncRetryableChunkProcessor",
    # Convenience
    "process_with_retry",
]
