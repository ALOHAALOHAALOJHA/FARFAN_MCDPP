from typing import Any, Dict, Optional, List
from dataclasses import dataclass

class MethodRegistry:
    def __init__(self, methods_dir: str, enable_lazy_loading: bool = True, enable_caching: bool = True):
        self.methods: Dict[str, Any] = {}

    def register(self, method_name: str, method_info: Any):
        self.methods[method_name] = method_info

    def load_all_methods(self):
        pass

    def get_all_methods(self) -> Dict[str, Any]:
        return self.methods
    
    def get_used_methods(self) -> List[str]:
        return list(self.methods.keys())

@dataclass
class Contract:
    contract_id: str
    question_id: str
    metadata: Any
    method_binding: Any

class ContractLoader:
    def __init__(self, contracts_dir: str, enable_validation: bool = True):
        self.contracts: List[Contract] = []

    def load_all_contracts(self) -> List[Contract]:
        return self.contracts
    
    def get_all_contracts(self) -> List[Contract]:
        return self.contracts

class ExecutorFactory:
    def __init__(
        self,
        method_registry: MethodRegistry,
        contract_loader: ContractLoader,
        questionnaire_provider: Any,
        sisas_central: Any,
        enable_parallel: bool = True,
        max_workers: int = 4,
    ):
        self.method_registry = method_registry
        self.contract_loader = contract_loader
    
    def execute_contract(self, contract: Any, chunk: Any, context: Dict[str, Any]) -> Any:
        # Mock execution result
        return type('TaskResult', (), {'signals': []})()

    def get_all_executors(self):
        return []
