"""Chunk Processor with Exponential Backoff - Minor Improvement 4.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Chunk Processor
PHASE_ROLE: Process document chunks with retry and error handling

Minor Improvement 4: Exponential Backoff for Failed Chunks

This module provides chunk processing with:
- Exponential backoff retry for transient failures
- Configurable retry parameters
- Detailed error tracking and metrics
- Partial success handling

Retry Strategy:
    - Base delay: 1 second
    - Multiplier: 2x for each retry
    - Max retries: 4 (delays: 1s, 2s, 4s, 8s)
    - Jitter: ±10% to prevent thundering herd
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# === EXCEPTIONS ===

class TransientError(Exception):
    """Raised for transient errors that may succeed on retry."""
    pass


class PermanentError(Exception):
    """Raised for permanent errors that should not be retried."""
    pass


class ChunkProcessingError(Exception):
    """Raised when chunk processing fails after all retries."""
    def __init__(self, chunk_id: str, attempts: int, last_error: str):
        self.chunk_id = chunk_id
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(
            f"Chunk {chunk_id} failed after {attempts} attempts: {last_error}"
        )


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
    metadata: Dict[str, Any] = field(default_factory=dict)


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
    error: Optional[str] = None
    attempts: int = 1
    total_time_ms: float = 0.0


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        base_delay_seconds: Initial delay between retries
        multiplier: Delay multiplier for each retry
        max_delay_seconds: Maximum delay cap
        jitter_factor: Random jitter factor (0.0 to 1.0)
    """
    max_retries: int = 4
    base_delay_seconds: float = 1.0
    multiplier: float = 2.0
    max_delay_seconds: float = 60.0
    jitter_factor: float = 0.1


@dataclass
class ProcessingMetrics:
    """Metrics for chunk processing.

    Attributes:
        total_chunks: Total chunks processed
        successful_chunks: Chunks that succeeded
        failed_chunks: Chunks that failed after all retries
        total_retries: Total retry attempts across all chunks
        total_time_ms: Total processing time
    """
    total_chunks: int = 0
    successful_chunks: int = 0
    failed_chunks: int = 0
    total_retries: int = 0
    total_time_ms: float = 0.0


# === CHUNK PROCESSOR ===

class RetryableChunkProcessor:
    """
    Processes chunks with exponential backoff retry.

    Minor Improvement 4: Exponential Backoff for Failed Chunks

    Features:
        - Configurable exponential backoff
        - Distinguishes transient vs permanent errors
        - Jitter to prevent thundering herd
        - Detailed metrics and logging
    """

    def __init__(
        self,
        processor_func: Callable[[Chunk], Any],
        config: RetryConfig | None = None
    ):
        """
        Initialize chunk processor.

        Args:
            processor_func: Function to process each chunk.
            config: Retry configuration.
        """
        self.processor_func = processor_func
        self.config = config or RetryConfig()
        self._metrics = ProcessingMetrics()

    def process_chunk(self, chunk: Chunk) -> ChunkResult:
        """
        Process a single chunk with retry logic.

        Args:
            chunk: Chunk to process.

        Returns:
            ChunkResult with processing outcome.
        """
        start_time = time.perf_counter()
        attempts = 0
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            attempts = attempt + 1

            try:
                output = self.processor_func(chunk)

                # Success
                total_time = (time.perf_counter() - start_time) * 1000
                self._metrics.total_chunks += 1
                self._metrics.successful_chunks += 1
                self._metrics.total_retries += attempt  # Retries = attempts - 1
                self._metrics.total_time_ms += total_time

                if attempt > 0:
                    logger.info(
                        f"Chunk {chunk.chunk_id} succeeded on attempt {attempts}"
                    )

                return ChunkResult(
                    chunk_id=chunk.chunk_id,
                    success=True,
                    output=output,
                    attempts=attempts,
                    total_time_ms=total_time,
                )

            except PermanentError as e:
                # Permanent error - don't retry
                logger.error(
                    f"Chunk {chunk.chunk_id} permanent error: {e}"
                )
                last_error = str(e)
                break

            except (TransientError, Exception) as e:
                last_error = str(e)

                if attempt == self.config.max_retries:
                    # Final attempt failed
                    logger.error(
                        f"Chunk {chunk.chunk_id} failed after {attempts} attempts: {e}"
                    )
                    break

                # Calculate delay with exponential backoff and jitter
                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Chunk {chunk.chunk_id} failed (attempt {attempts}), "
                    f"retrying in {delay:.2f}s: {e}"
                )
                time.sleep(delay)

        # All retries exhausted
        total_time = (time.perf_counter() - start_time) * 1000
        self._metrics.total_chunks += 1
        self._metrics.failed_chunks += 1
        self._metrics.total_retries += attempts - 1
        self._metrics.total_time_ms += total_time

        return ChunkResult(
            chunk_id=chunk.chunk_id,
            success=False,
            error=last_error,
            attempts=attempts,
            total_time_ms=total_time,
        )

    def process_chunks(self, chunks: List[Chunk]) -> List[ChunkResult]:
        """
        Process multiple chunks.

        Args:
            chunks: List of chunks to process.

        Returns:
            List of ChunkResult objects.
        """
        results = []
        for i, chunk in enumerate(chunks):
            logger.debug(f"Processing chunk {i + 1}/{len(chunks)}: {chunk.chunk_id}")
            result = self.process_chunk(chunk)
            results.append(result)

        successful = sum(1 for r in results if r.success)
        logger.info(
            f"Processed {len(chunks)} chunks: "
            f"{successful} succeeded, {len(chunks) - successful} failed"
        )

        return results

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry attempt.

        Uses exponential backoff with jitter:
            delay = base * (multiplier ^ attempt) * (1 + random_jitter)

        Args:
            attempt: Current attempt number (0-indexed).

        Returns:
            Delay in seconds.
        """
        # Exponential backoff
        delay = self.config.base_delay_seconds * (self.config.multiplier ** attempt)

        # Cap at max delay
        delay = min(delay, self.config.max_delay_seconds)

        # Add jitter
        if self.config.jitter_factor > 0:
            jitter = delay * self.config.jitter_factor * random.uniform(-1, 1)
            delay = max(0, delay + jitter)

        return delay

    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics."""
        total = self._metrics.total_chunks or 1
        return {
            "total_chunks": self._metrics.total_chunks,
            "successful_chunks": self._metrics.successful_chunks,
            "failed_chunks": self._metrics.failed_chunks,
            "success_rate": self._metrics.successful_chunks / total,
            "total_retries": self._metrics.total_retries,
            "avg_retries_per_chunk": self._metrics.total_retries / total,
            "total_time_ms": self._metrics.total_time_ms,
            "avg_time_per_chunk_ms": self._metrics.total_time_ms / total,
        }

    def reset_metrics(self) -> None:
        """Reset processing metrics."""
        self._metrics = ProcessingMetrics()


# === ASYNC CHUNK PROCESSOR ===

class AsyncRetryableChunkProcessor:
    """
    Async version of chunk processor with exponential backoff.

    Use this when processing chunks with async I/O operations.
    """

    def __init__(
        self,
        processor_func: Callable[[Chunk], Any],
        config: RetryConfig | None = None
    ):
        """
        Initialize async chunk processor.

        Args:
            processor_func: Async function to process each chunk.
            config: Retry configuration.
        """
        self.processor_func = processor_func
        self.config = config or RetryConfig()
        self._metrics = ProcessingMetrics()

    async def process_chunk(self, chunk: Chunk) -> ChunkResult:
        """Process a single chunk asynchronously with retry."""
        import asyncio

        start_time = time.perf_counter()
        attempts = 0
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            attempts = attempt + 1

            try:
                output = await self.processor_func(chunk)

                total_time = (time.perf_counter() - start_time) * 1000
                self._metrics.total_chunks += 1
                self._metrics.successful_chunks += 1
                self._metrics.total_retries += attempt
                self._metrics.total_time_ms += total_time

                return ChunkResult(
                    chunk_id=chunk.chunk_id,
                    success=True,
                    output=output,
                    attempts=attempts,
                    total_time_ms=total_time,
                )

            except PermanentError as e:
                last_error = str(e)
                break

            except (TransientError, Exception) as e:
                last_error = str(e)

                if attempt == self.config.max_retries:
                    break

                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Chunk {chunk.chunk_id} failed (attempt {attempts}), "
                    f"retrying in {delay:.2f}s: {e}"
                )
                await asyncio.sleep(delay)

        total_time = (time.perf_counter() - start_time) * 1000
        self._metrics.total_chunks += 1
        self._metrics.failed_chunks += 1
        self._metrics.total_retries += attempts - 1
        self._metrics.total_time_ms += total_time

        return ChunkResult(
            chunk_id=chunk.chunk_id,
            success=False,
            error=last_error,
            attempts=attempts,
            total_time_ms=total_time,
        )

    async def process_chunks(self, chunks: List[Chunk]) -> List[ChunkResult]:
        """Process multiple chunks concurrently."""
        import asyncio

        tasks = [self.process_chunk(chunk) for chunk in chunks]
        return await asyncio.gather(*tasks)

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = self.config.base_delay_seconds * (self.config.multiplier ** attempt)
        delay = min(delay, self.config.max_delay_seconds)

        if self.config.jitter_factor > 0:
            jitter = delay * self.config.jitter_factor * random.uniform(-1, 1)
            delay = max(0, delay + jitter)

        return delay

    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics."""
        total = self._metrics.total_chunks or 1
        return {
            "total_chunks": self._metrics.total_chunks,
            "successful_chunks": self._metrics.successful_chunks,
            "failed_chunks": self._metrics.failed_chunks,
            "success_rate": self._metrics.successful_chunks / total,
            "total_retries": self._metrics.total_retries,
            "total_time_ms": self._metrics.total_time_ms,
        }


# === CONVENIENCE FUNCTIONS ===

def process_with_retry(
    func: Callable[[], T],
    max_retries: int = 4,
    base_delay: float = 1.0
) -> T:
    """
    Execute a function with exponential backoff retry.

    Args:
        func: Function to execute.
        max_retries: Maximum retry attempts.
        base_delay: Base delay between retries.

    Returns:
        Function result.

    Raises:
        Exception: If all retries fail.
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except PermanentError:
            raise
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                delay += delay * 0.1 * random.uniform(-1, 1)
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}"
                )
                time.sleep(delay)

    if last_error is None:
        # This should not normally happen; indicates no attempts were made or no exception was captured.
        raise RuntimeError("process_with_retry failed without capturing an error")

    raise last_error


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
    "ProcessingMetrics",
    # Processors
    "RetryableChunkProcessor",
    "AsyncRetryableChunkProcessor",
    # Convenience
    "process_with_retry",
]
