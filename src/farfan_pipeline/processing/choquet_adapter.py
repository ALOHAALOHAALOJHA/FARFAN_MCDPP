"""Stub for choquet_adapter to allow imports."""

class ChoquetProcessingAdapter:
    def __init__(self, n_layers):
        self.n_layers = n_layers
    
    def aggregate(self, scores, weights=None):
        if weights is None:
            return sum(scores) / len(scores) if scores else 0.0
        return sum(s * w for s, w in zip(scores, weights))

def create_default_choquet_adapter(n_layers):
    return ChoquetProcessingAdapter(n_layers)
