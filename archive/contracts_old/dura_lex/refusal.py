"""
Refusal Contract (RefC) - Implementation
"""
from typing import Dict, Any

class RefusalError(Exception):
    pass

class RefusalContract:
    @staticmethod
    def check_prerequisites(context: Dict[str, Any]):
        """
        Confirma que ante prerequisitos fallidos el sistema rehúsa con motivo tipado.
        """
        if "mandatory" not in context:
            raise RefusalError("Missing mandatory field")
            
        if context.get("alpha", 1.0) > 0.5:
             raise RefusalError("Alpha violation")
             
        if "sigma" not in context:
            raise RefusalError("Sigma absent")

    @staticmethod
    def verify_refusal(context: Dict[str, Any]) -> str:
        try:
            RefusalContract.check_prerequisites(context)
            return "OK"
        except RefusalError as e:
            return str(e)
