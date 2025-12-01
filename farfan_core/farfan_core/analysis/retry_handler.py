from enum import Enum
import time
import logging
from functools import wraps

class DependencyType(Enum):
    SPACY_MODEL = "spaCy_model"
    PDF_PARSER = "pdf_parser"

def get_retry_handler():
    return RetryHandler()

class RetryHandler:
    def __init__(self, max_retries=3, delay=1):
        self.max_retries = max_retries
        self.delay = delay
        self.logger = logging.getLogger(self.__class__.__name__)

    def with_retry(self, dependency_type, operation_name, exceptions):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                retries = 0
                while retries < self.max_retries:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        retries += 1
                        self.logger.warning(
                            f"Operation '{operation_name}' for dependency '{dependency_type.value}' failed. "
                            f"Retrying ({retries}/{self.max_retries})... Error: {e}"
                        )
                        time.sleep(self.delay)
                self.logger.error(
                    f"Operation '{operation_name}' for dependency '{dependency_type.value}' "
                    f"failed after {self.max_retries} retries."
                )
                raise
            return wrapper
        return decorator
