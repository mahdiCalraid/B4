import asyncio
import logging
import uuid
from typing import Dict, List, Any
from datetime import datetime
from runners.base import ExecutionContext, BaseNodeRunner
from registry import registry
import importlib

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """Orchestrates the execution of a workflow."""
    
    def __init__(self):
        self.executions: Dict[str, ExecutionContext] = {}

    async def execute_workflow(self, workflow: Dict[str, Any]) -> str:
        """
        Execute a full workflow.
        
        Args:
            workflow: The workflow dictionary (matching workflow_schema.json).
            
        Returns:
            execution_id: The ID of the started execution.
        """
        execution_id = str(uuid.uuid4())
        context = ExecutionContext(execution_id)
        context.logs = []  # Initialize logs list
        self.executions[execution_id] = context
        
        # Log workflow start
        context.logs.append({
            "timestamp": datetime.now().isoformat(),
            "message": f"🚀 Starting workflow execution",
            "details": {"workflow_id": workflow.get("id"), "node_count": len(workflow.get("nodes", []))}
        })
        
        # Run in background
        asyncio.create_task(self._run_graph(workflow, context))
        
        return execution_id

    async def _run_graph(self, workflow: Dict[str, Any], context: ExecutionContext):
        """Internal method to run the graph (Topological Sort + Execution)."""
        try:
            nodes = {n["id"]: n for n in workflow["nodes"]}
            edges = workflow["edges"]
            
            # 1. Build Dependency Graph
            adj = {n: [] for n in nodes}
            in_degree = {n: 0 for n in nodes}
            
            for edge in edges:
                src = edge["source"]
                tgt = edge["target"]
                if src in nodes and tgt in nodes:
                    adj[src].append(tgt)
                    in_degree[tgt] += 1
            
            # 2. Topological Sort (Kahn's Algorithm)
            queue = [n for n in nodes if in_degree[n] == 0]
            execution_order = []
            
            while queue:
                u = queue.pop(0)
                execution_order.append(u)
                
                for v in adj[u]:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        queue.append(v)
            
            if len(execution_order) != len(nodes):
                raise ValueError("Cycle detected in workflow graph")
            
            context.logs.append({
                "timestamp": datetime.now().isoformat(),
                "message": f"📋 Execution order determined: {len(execution_order)} nodes",
                "details": {"order": execution_order}
            })
            
            # 3. Execute Nodes in Order
            for node_id in execution_order:
                node_instance = nodes[node_id]
                await self._execute_node(node_instance, context, edges)
                
            context.state = "completed"
            context.logs.append({
                "timestamp": datetime.now().isoformat(),
                "message": "✅ Workflow completed successfully"
            })
            logger.info(f"Execution {context.execution_id} completed successfully.")
            
        except Exception as e:
            context.state = "failed"
            context.error = str(e)
            context.logs.append({
                "timestamp": datetime.now().isoformat(),
                "message": f"❌ Workflow failed: {str(e)}"
            })
            logger.error(f"Execution {context.execution_id} failed: {e}")

    async def _execute_node(self, instance: Dict[str, Any], context: ExecutionContext, edges: List[Dict]):
        """Execute a single node instance."""
        node_id = instance["id"]
        node_def_id = instance.get("type") or instance.get("data", {}).get("type")
        node_label = instance.get("data", {}).get("label", node_id)
        
        context.logs.append({
            "timestamp": datetime.now().isoformat(),
            "message": f"▶️  Executing: {node_label}",
            "details": {"node_id": node_id, "type": node_def_id}
        })
        
        # 1. Get Node Definition from Registry
        node_def = next((n for n in registry.list_nodes() if n["id"] == node_def_id), None)
        if not node_def:
            error_msg = f"Node definition not found for type: {node_def_id}"
            context.logs.append({
                "timestamp": datetime.now().isoformat(),
                "message": f"⚠️  {error_msg}"
            })
            raise ValueError(error_msg)
            
        runner_path = node_def.get("runner")
        if not runner_path:
            error_msg = f"No runner defined for node type: {node_def_id}"
            context.logs.append({
                "timestamp": datetime.now().isoformat(),
                "message": f"⚠️  {error_msg}"
            })
            raise ValueError(error_msg)
            
        # 2. Instantiate Runner
        runner = self._load_runner(runner_path)
        
        # 3. Resolve Inputs
        inputs = self._resolve_inputs(node_id, context, edges)
        
        context.logs.append({
            "timestamp": datetime.now().isoformat(),
            "message": f"📥 Input for {node_label}",
            "details": inputs
        })
        
        # 4. Run
        config = instance.get("data", {}).get("config", {}).copy()
        # Also pass text from data if it exists (for Text Input nodes)
        if "text" in instance.get("data", {}):
            inputs["text"] = instance["data"]["text"]
        
        config["_node_def"] = node_def
        logger.info(f"Running node {node_id} ({node_def_id})")
        
        output = await runner.run(config, inputs, context)
        
        # 5. Store Output
        context.set_output(node_id, output)
        
        context.logs.append({
            "timestamp": datetime.now().isoformat(),
            "message": f"📤 Output from {node_label}",
            "details": output
        })

    def _resolve_inputs(self, node_id: str, context: ExecutionContext, edges: List[Dict]) -> Dict[str, Any]:
        """Collect outputs from upstream nodes."""
        inputs = {}
        # Find all edges pointing TO this node
        incoming_edges = [e for e in edges if e["target"] == node_id]
        
        for edge in incoming_edges:
            source_id = edge["source"]
            source_output = context.get_output(source_id)
            
            # In a real system, we'd map specific output keys to input keys based on handles.
            # For now, we merge all upstream outputs.
            if isinstance(source_output, dict):
                inputs.update(source_output)
                
        return inputs

    def _load_runner(self, runner_path: str) -> BaseNodeRunner:
        """Dynamically load the runner class."""
        module_name, class_name = runner_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        runner_class = getattr(module, class_name)
        return runner_class()

# Global Engine Instance
engine = ExecutionEngine()
