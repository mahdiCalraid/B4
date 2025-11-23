"""
Simple waterfall orchestrator with integrated logging.
Shows how agents work together in the pipeline.
"""

from typing import Dict, Any, Optional
import asyncio
from agents.agent_loader import AgentLoader
from agents.general_codes.waterfall_logger import get_waterfall_logger

class SimpleWaterfallOrchestrator:
    """
    Orchestrates agents through the waterfall pipeline with logging.
    """

    def __init__(self):
        self.loader = AgentLoader()
        self.logger = get_waterfall_logger()

        # Define the waterfall stages
        self.stages = [
            # Stage 1: Attention
            {"agent": "attention_filter", "model": "gpt-oss-20b", "required": True},

            # Stage 2: Context (when created)
            # {"agent": "context_builder", "model": "gemini-2.0-flash-lite", "required": False},

            # Stage 3: Extraction (parallel in future)
            {"agent": "agent_mother", "model": "gemini-2.0-flash", "required": False},

            # Add more stages as agents are created
        ]

    async def process(self, input_text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process input through the waterfall pipeline.

        Args:
            input_text: Input to process
            metadata: Optional metadata

        Returns:
            Final result from pipeline
        """
        # Start pipeline logging
        self.logger.start_processing(input_text, metadata)

        # Track results from each stage
        stage_results = {}
        should_continue = True

        try:
            for stage in self.stages:
                if not should_continue:
                    break

                agent_id = stage["agent"]
                model = stage["model"]
                required = stage.get("required", False)

                try:
                    # Load agent
                    agent = self.loader.load_agent(agent_id)

                    # Process with agent
                    result = await agent.process(
                        input_data=input_text,
                        model=model
                    )

                    # Store result
                    stage_results[agent_id] = result

                    # Check if we should continue (attention filter decision)
                    if agent_id == "attention_filter":
                        should_process = result.get("should_process", True)
                        if not should_process:
                            self.logger.agent_step(
                                agent_id,
                                "Pipeline stopped",
                                {"reason": result.get("skip_reason", "Unknown")}
                            )
                            should_continue = False

                except Exception as e:
                    if required:
                        # Required agent failed, stop pipeline
                        self.logger.agent_error(agent_id, f"Required agent failed: {e}", e)
                        raise
                    else:
                        # Optional agent failed, continue
                        self.logger.agent_error(agent_id, f"Optional agent failed: {e}", e)
                        stage_results[agent_id] = {"error": str(e)}

            # Complete pipeline
            self.logger.pipeline_complete(stage_results)

            # Return aggregated results
            return {
                "processed": should_continue,
                "stages_completed": len(stage_results),
                "results": stage_results,
                "trace": self.logger.get_trace()
            }

        except Exception as e:
            self.logger.pipeline_complete({"error": str(e)})
            raise

    async def process_batch(self, inputs: list) -> list:
        """
        Process multiple inputs through the pipeline.

        Args:
            inputs: List of input texts

        Returns:
            List of results
        """
        results = []
        for input_text in inputs:
            result = await self.process(input_text)
            results.append(result)
        return results