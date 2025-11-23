"""
Centralized logging system for the B4 waterfall pipeline.
All agents use this logger to track their processing steps.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import asyncio
from collections import deque

class WaterfallLogger:
    """
    Centralized logger for all agents in the waterfall pipeline.
    Tracks the flow of data through each agent with detailed logging.
    """

    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        Initialize the waterfall logger.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional file path to write logs
        """
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file

        # Setup Python logger
        self.logger = logging.getLogger("waterfall")
        self.logger.setLevel(self.log_level)

        # Console handler with formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)

        # Custom formatter for waterfall
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # In-memory log buffer for recent events
        self.log_buffer = deque(maxlen=100)

        # Processing trace for current input
        self.current_trace = []
        self.current_input = None

    def start_processing(self, input_text: str, metadata: Optional[Dict] = None):
        """
        Start tracking a new input through the pipeline.

        Args:
            input_text: The input being processed
            metadata: Optional metadata about the input
        """
        self.current_input = input_text[:100] + "..." if len(input_text) > 100 else input_text
        self.current_trace = []

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "pipeline_start",
            "input": self.current_input,
            "metadata": metadata
        }

        self.log_buffer.append(log_entry)
        self.logger.info(f"🚀 PIPELINE START: {self.current_input}")

        if metadata:
            self.logger.debug(f"   Metadata: {metadata}")

    def agent_start(self, agent_id: str, model: Optional[str] = None):
        """
        Log when an agent starts processing.

        Args:
            agent_id: The agent identifier
            model: The AI model being used
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "agent_start",
            "agent": agent_id,
            "model": model
        }

        self.current_trace.append(log_entry)
        self.log_buffer.append(log_entry)

        self.logger.info(f"📍 [{agent_id}] Starting processing" +
                        (f" with {model}" if model else ""))

    def agent_step(self, agent_id: str, step: str, details: Any = None):
        """
        Log a specific step within an agent's processing.

        Args:
            agent_id: The agent identifier
            step: Description of the step
            details: Optional details about the step
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "agent_step",
            "agent": agent_id,
            "step": step,
            "details": details
        }

        self.current_trace.append(log_entry)
        self.log_buffer.append(log_entry)

        if details:
            if isinstance(details, dict):
                details_str = json.dumps(details, indent=2)
            else:
                details_str = str(details)
            self.logger.debug(f"   [{agent_id}] {step}: {details_str}")
        else:
            self.logger.debug(f"   [{agent_id}] {step}")

    def agent_result(self, agent_id: str, result: Dict[str, Any]):
        """
        Log the result from an agent.

        Args:
            agent_id: The agent identifier
            result: The agent's output
        """
        # Extract key information from result
        summary = self._summarize_result(result)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "agent_result",
            "agent": agent_id,
            "summary": summary,
            "result": result
        }

        self.current_trace.append(log_entry)
        self.log_buffer.append(log_entry)

        self.logger.info(f"✅ [{agent_id}] Completed: {summary}")

    def agent_error(self, agent_id: str, error: str, exception: Optional[Exception] = None):
        """
        Log an error from an agent.

        Args:
            agent_id: The agent identifier
            error: Error message
            exception: Optional exception object
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "agent_error",
            "agent": agent_id,
            "error": error,
            "exception": str(exception) if exception else None
        }

        self.current_trace.append(log_entry)
        self.log_buffer.append(log_entry)

        self.logger.error(f"❌ [{agent_id}] ERROR: {error}")

        if exception:
            self.logger.exception(exception)

    def pipeline_complete(self, final_result: Any = None):
        """
        Log pipeline completion.

        Args:
            final_result: The final output from the pipeline
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "pipeline_complete",
            "input": self.current_input,
            "trace_length": len(self.current_trace),
            "final_result": final_result
        }

        self.log_buffer.append(log_entry)
        self.logger.info(f"🏁 PIPELINE COMPLETE: {len(self.current_trace)} steps executed")

    def get_trace(self) -> List[Dict]:
        """
        Get the processing trace for the current input.

        Returns:
            List of log entries for current processing
        """
        return self.current_trace

    def get_recent_logs(self, count: int = 50) -> List[Dict]:
        """
        Get recent log entries from the buffer.

        Args:
            count: Number of recent logs to retrieve

        Returns:
            List of recent log entries
        """
        return list(self.log_buffer)[-count:]

    def _summarize_result(self, result: Dict[str, Any]) -> str:
        """
        Create a summary of an agent's result.

        Args:
            result: The agent's output

        Returns:
            Summary string
        """
        summary_parts = []

        # Common fields to summarize
        if "should_process" in result:
            summary_parts.append(f"process={result['should_process']}")

        if "relevance_score" in result:
            summary_parts.append(f"relevance={result['relevance_score']:.2f}")

        if "importance_score" in result:
            summary_parts.append(f"importance={result['importance_score']:.2f}")

        if "entities" in result and isinstance(result["entities"], list):
            summary_parts.append(f"entities={len(result['entities'])}")

        if "entity_hints" in result and isinstance(result["entity_hints"], list):
            summary_parts.append(f"entities={len(result['entity_hints'])}")

        if not summary_parts and isinstance(result, dict):
            # Generic summary for unknown structure
            summary_parts.append(f"fields={len(result)}")

        return ", ".join(summary_parts) if summary_parts else "completed"

    def format_waterfall_report(self) -> str:
        """
        Format a detailed report of the current processing trace.

        Returns:
            Formatted report string
        """
        if not self.current_trace:
            return "No processing trace available"

        report = []
        report.append("=" * 60)
        report.append("WATERFALL PROCESSING REPORT")
        report.append("=" * 60)
        report.append(f"Input: {self.current_input}")
        report.append(f"Steps: {len(self.current_trace)}")
        report.append("-" * 60)

        current_agent = None
        for entry in self.current_trace:
            if entry["event"] == "agent_start":
                current_agent = entry["agent"]
                report.append(f"\n📍 AGENT: {current_agent}")
                if entry.get("model"):
                    report.append(f"   Model: {entry['model']}")

            elif entry["event"] == "agent_step":
                report.append(f"   • {entry['step']}")
                if entry.get("details"):
                    report.append(f"     {entry['details']}")

            elif entry["event"] == "agent_result":
                report.append(f"   ✓ Result: {entry['summary']}")

            elif entry["event"] == "agent_error":
                report.append(f"   ✗ Error: {entry['error']}")

        report.append("-" * 60)
        return "\n".join(report)


# Global logger instance
_logger_instance = None

def get_waterfall_logger() -> WaterfallLogger:
    """
    Get or create the global waterfall logger instance.

    Returns:
        WaterfallLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        # Configure based on environment
        import os
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file = os.getenv("WATERFALL_LOG_FILE", "/tmp/b4_waterfall.log")

        _logger_instance = WaterfallLogger(
            log_level=log_level,
            log_file=log_file
        )

    return _logger_instance