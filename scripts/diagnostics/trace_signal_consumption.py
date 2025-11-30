#!/usr/bin/env python3
"""
trace_signal_consumption.py - Trace the consumption of signals for a single micro-question.

This script demonstrates the signal consumption flow by executing a single
micro-question and capturing the structured logs related to signal usage.
"""

import asyncio
import json
import sys
from pathlib import Path
import structlog

# Add src to python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from farfan_core.core.orchestrator.factory import build_processor
from farfan_core.core.orchestrator.core import PreprocessedDocument, Evidence

def setup_logging():
    """
    Configure structlog to print to the console.
    """
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(min_level=structlog.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_micro_question_by_slot(monolith: dict, base_slot: str) -> dict:
    """
    Finds and returns the first micro-question with the given base_slot.
    """
    def find_in_obj(obj):
        if isinstance(obj, dict):
            if "micro_questions" in obj and isinstance(obj["micro_questions"], list):
                for q in obj["micro_questions"]:
                    if q.get("base_slot") == base_slot:
                        return q
            for value in obj.values():
                result = find_in_obj(value)
                if result:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = find_in_obj(item)
                if result:
                    return result
        return None
    
    return find_in_obj(monolith)


async def main():
    """
    Main function to run the signal consumption trace.
    """
    setup_logging()
    log = structlog.get_logger()

    log.info("--- Starting Signal Consumption Trace ---")

    # 1. Build the processor bundle
    log.info("Building processor bundle...")
    try:
        processor_bundle = build_processor()
    except Exception as e:
        log.error("Failed to build processor bundle", error=str(e))
        return

    method_executor = processor_bundle.method_executor
    questionnaire = processor_bundle.questionnaire
    
    # 2. Get a micro-question
    base_slot_to_trace = "D1-Q1"
    log.info(f"Getting micro-question for base_slot: {base_slot_to_trace}")
    micro_question = get_micro_question_by_slot(questionnaire.data, base_slot_to_trace)
    if not micro_question:
        log.error("Micro-question not found", base_slot=base_slot_to_trace)
        return

    # 3. Create a dummy document
    log.info("Creating a dummy document for execution...")
    dummy_doc = PreprocessedDocument(
        document_id="dummy-doc",
        raw_text="This is a test document about policy and finance.",
        sentences=["This is a test document about policy and finance."],
        tables=[],
        metadata={"source": "dummy"},
    )
    
    # 4. Get the executor instance from the orchestrator
    # We need to instantiate the orchestrator to get the executor mapping
    try:
        from farfan_core.core.orchestrator.core import Orchestrator
        orchestrator = Orchestrator(
            method_executor=method_executor,
            questionnaire=questionnaire,
            executor_config=processor_bundle.executor_config
        )
        executor_class = orchestrator.executors.get(base_slot_to_trace)
        if not executor_class:
            log.error("Executor not found for base_slot", base_slot=base_slot_to_trace)
            return
            
        executor_instance = executor_class(
            method_executor,
            signal_registry=processor_bundle.signal_registry,
            config=processor_bundle.executor_config,
            questionnaire_provider=None, # Not strictly needed for this trace
        )

    except Exception as e:
        log.error("Failed to instantiate orchestrator or executor", error=str(e))
        return

    # 5. Execute the question
    log.info("Executing the micro-question...", question_id=micro_question.get("question_id"))
    try:
        evidence: Evidence = await asyncio.to_thread(
            executor_instance.execute,
            dummy_doc,
            method_executor,
            question_context=micro_question
        )
        log.info("Execution successful.", evidence_keys=list(evidence.keys()))
    except Exception as e:
        log.error("Execution failed", error=str(e), exc_info=True)

    log.info("--- Signal Consumption Trace Complete ---")


if __name__ == "__main__":
    asyncio.run(main())
