"""
Concurrency Determinism Contract (CDC) - Implementation
"""
import hashlib
import json
import threading
import time
from typing import List, Any, Callable

class ConcurrencyDeterminismContract:
    @staticmethod
    def execute_concurrently(
        func: Callable[[Any], Any], 
        inputs: List[Any], 
        workers: int
    ) -> List[Any]:
        """
        Simulates concurrent execution.
        To ensure determinism, results must be sorted or indexed by input ID.
        """
        results = [None] * len(inputs)
        
        def worker(idx, inp):
            # Simulate work
            time.sleep(0.001)
            results[idx] = func(inp)
            
        threads = []
        for i, inp in enumerate(inputs):
            t = threading.Thread(target=worker, args=(i, inp))
            threads.append(t)
            t.start()
            
            if len(threads) >= workers:
                for t in threads:
                    t.join()
                threads = []
                
        for t in threads:
            t.join()
            
        return results

    @staticmethod
    def verify_determinism(
        func: Callable[[Any], Any], 
        inputs: List[Any]
    ) -> bool:
        """
        Verifies that 1 worker vs N workers produces hash-equal outputs.
        """
        res_seq = ConcurrencyDeterminismContract.execute_concurrently(func, inputs, workers=1)
        res_conc = ConcurrencyDeterminismContract.execute_concurrently(func, inputs, workers=4)
        
        hash1 = hashlib.blake2b(json.dumps(res_seq, sort_keys=True).encode()).hexdigest()
        hash2 = hashlib.blake2b(json.dumps(res_conc, sort_keys=True).encode()).hexdigest()
        
        return hash1 == hash2
