"""
Deterministic Seed Factory
Generates reproducible seeds for all stochastic operations
"""

import hashlib
import hmac
import random
from typing import Any

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None  # type: ignore

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None  # type: ignore

class SeedFactory:
    """
    Factory for generating deterministic seeds

    Ensures:
    - Reproducibility: Same inputs → same seed
    - Uniqueness: Different contexts → different seeds
    - Cryptographic quality: HMAC-SHA256 derivation
    """

    # Fixed salt for seed derivation (should be configured per deployment)
    DEFAULT_SALT = b"PDM_EVALUATOR_V2_DETERMINISTIC_SEED_2025"

    def __init__(self, fixed_salt: bytes | None = None) -> None:
        self.salt = fixed_salt or self.DEFAULT_SALT

    def create_deterministic_seed(
        self,
        correlation_id: str,
        file_checksums: dict[str, str] | None = None,
        context: dict[str, Any] | None = None
    ) -> int:
        """
        Generate deterministic seed from correlation ID and context

        Args:
            correlation_id: Unique workflow instance identifier
            file_checksums: Dict of {filename: sha256_checksum}
            context: Additional context (question_id, policy_area, etc.)

        Returns:
            32-bit integer seed (0 to 2^32-1)

        Example:
            >>> factory = SeedFactory()
            >>> seed1 = factory.create_deterministic_seed("run-001", {"data.json": "abc123"})
            >>> seed2 = factory.create_deterministic_seed("run-001", {"data.json": "abc123"})
            >>> assert seed1 == seed2  # Reproducible
        """

        # Build deterministic input string
        components = [correlation_id]

        # Add file checksums (sorted for determinism)
        if file_checksums:
            sorted_checksums = sorted(file_checksums.items())
            for filename, checksum in sorted_checksums:
                components.append(f"{filename}:{checksum}")

        # Add context (sorted for determinism)
        if context:
            sorted_context = sorted(context.items())
            for key, value in sorted_context:
                components.append(f"{key}={value}")

        # Combine with deterministic separator
        seed_input = "|".join(components).encode('utf-8')

        # HMAC-SHA256 for cryptographic quality
        seed_hmac = hmac.new(
            key=self.salt,
            msg=seed_input,
            digestmod=hashlib.sha256
        )

        # Convert to 32-bit integer
        seed_bytes = seed_hmac.digest()[:4]  # First 4 bytes
        seed_int = int.from_bytes(seed_bytes, byteorder='big')

        return seed_int

    def configure_global_random_state(self, seed: int) -> None:
        """
        Configure all random number generators with seed

        Sets:
        - Python random module
        - NumPy random state
        - PyTorch (manual_seed, CUDA, deterministic)
        - TensorFlow (random.set_seed)

        Args:
            seed: Deterministic seed

        Note:
            PyTorch and TensorFlow operations will be deterministic when
            these frameworks are available. This ensures reproducibility
            across all stochastic operations in the pipeline.
        """

        # Python random module
        random.seed(seed)

        # NumPy
        if NUMPY_AVAILABLE and np is not None:
            np.random.seed(seed)

        # PyTorch: Set seed for CPU and CUDA operations
        if TORCH_AVAILABLE and torch is not None:
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)  # For all GPU devices
            # Enable deterministic algorithms (may impact performance)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

        # TensorFlow: Set global random seed
        if TENSORFLOW_AVAILABLE and tf is not None:
            tf.random.set_seed(seed)
            # For TensorFlow 2.x, also configure graph-level operations
            try:
                # Ensure deterministic behavior for TF ops
                tf.config.experimental.enable_op_determinism()
            except AttributeError:
                # Older TensorFlow versions may not have this
                pass

class DeterministicContext:
    """
    Context manager for deterministic execution

    Usage:
        with DeterministicContext(correlation_id="run-001") as seed:
            # All random operations are deterministic
            result = some_stochastic_function()
    """

    def __init__(
        self,
        correlation_id: str,
        file_checksums: dict[str, str] | None = None,
        context: dict[str, Any] | None = None,
        fixed_salt: bytes | None = None
    ) -> None:
        self.correlation_id = correlation_id
        self.file_checksums = file_checksums
        self.context = context
        self.factory = SeedFactory(fixed_salt=fixed_salt)

        self.seed: int | None = None
        self.previous_random_state = None
        self.previous_numpy_state = None
        self.previous_torch_state = None
        self.previous_cuda_state = None

    def __enter__(self) -> int:
        """Enter deterministic context"""

        # Generate deterministic seed
        self.seed = self.factory.create_deterministic_seed(
            correlation_id=self.correlation_id,
            file_checksums=self.file_checksums,
            context=self.context
        )

        # Save current random states
        self.previous_random_state = random.getstate()
        if NUMPY_AVAILABLE and np is not None:
            self.previous_numpy_state = np.random.get_state()

        # Save PyTorch state
        if TORCH_AVAILABLE and torch is not None:
            self.previous_torch_state = torch.get_rng_state()
            if torch.cuda.is_available():
                self.previous_cuda_state = torch.cuda.get_rng_state_all()

        # Configure with deterministic seed
        self.factory.configure_global_random_state(self.seed)

        return self.seed

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit deterministic context and restore previous state"""

        # Restore previous random states
        if self.previous_random_state:
            random.setstate(self.previous_random_state)

        if NUMPY_AVAILABLE and np is not None and self.previous_numpy_state:
            np.random.set_state(self.previous_numpy_state)

        # Restore PyTorch state
        if TORCH_AVAILABLE and torch is not None and self.previous_torch_state is not None:
            torch.set_rng_state(self.previous_torch_state)
            if torch.cuda.is_available() and self.previous_cuda_state is not None:
                torch.cuda.set_rng_state_all(self.previous_cuda_state)

        return False

def create_deterministic_seed(
    correlation_id: str,
    file_checksums: dict[str, str] | None = None,
    **context_kwargs
) -> int:
    """
    Convenience function for creating deterministic seed

    Args:
        correlation_id: Unique workflow instance ID
        file_checksums: Dict of file checksums
        **context_kwargs: Additional context as keyword arguments

    Returns:
        Deterministic 32-bit integer seed

    Example:
        >>> seed = create_deterministic_seed(
        ...     "run-001",
        ...     question_id="Q001",
        ...     policy_area_id="PA01"
        ... )
    """
    factory = SeedFactory()
    return factory.create_deterministic_seed(
        correlation_id=correlation_id,
        file_checksums=file_checksums,
        context=context_kwargs if context_kwargs else None
    )
