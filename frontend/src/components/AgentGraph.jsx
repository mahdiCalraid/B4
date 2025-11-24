import React, { useEffect, useCallback, useState, useRef } from 'react';
import ReactFlow, {
    useNodesState,
    useEdgesState,
    Background,
    Controls,
    addEdge,
    MarkerType,
    Handle,
    Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import { Undo2, Redo2 } from 'lucide-react';
import CustomNode from './CustomNode';
import TextInputNode from './TextInputNode';

const nodeTypes = {
    custom: CustomNode,
    textInput: TextInputNode
};

const nodeWidth = 250;
const nodeHeight = 100;

const getLayoutedElements = (nodes, edges, direction = 'LR') => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));

    dagreGraph.setGraph({ rankdir: direction });

    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    nodes.forEach((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        node.targetPosition = 'left';
        node.sourcePosition = 'right';

        // We are shifting the dagre node position (anchor=center center) to the top left
        // so it matches the React Flow node anchor point (top left).
        node.position = {
            x: nodeWithPosition.x - nodeWidth / 2,
            y: nodeWithPosition.y - nodeHeight / 2,
        };

        return node;
    });

    return { nodes, edges };
};

const AgentGraph = ({ traceData, workflowData, onNodeClick, onWorkflowChange, setLogs }) => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [reactFlowInstance, setReactFlowInstance] = React.useState(null);
    const [history, setHistory] = useState([]);
    const [historyIndex, setHistoryIndex] = useState(-1);

    // Refs to access current state in callbacks without dependency issues
    const nodesRef = useRef(nodes);
    const edgesRef = useRef(edges);

    useEffect(() => {
        nodesRef.current = nodes;
        edgesRef.current = edges;
    }, [nodes, edges]);

    useEffect(() => {
        // 1. Handle Workflow Definition (Editor Mode)
        if (workflowData) {
            const flowNodes = workflowData.nodes.map(node => ({
                id: node.id,
                position: node.position || { x: 0, y: 0 },
                data: {
                    ...(node.data || { label: node.id }),
                    onTextChange: handleTextInputChange,
                    onTrigger: handleTriggerWorkflow
                },
                type: (node.type === 'input-text' || node.type === 'textInput' || node.data?.type === 'input-text') ? 'textInput' : 'custom',
                style: {
                    background: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '16px',
                    minWidth: '200px',
                    textAlign: 'left',
                    color: '#1e293b',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    fontFamily: 'Inter, sans-serif',
                },
            }));

            const flowEdges = workflowData.edges.map(edge => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
                type: 'smoothstep',
                markerEnd: { type: MarkerType.ArrowClosed },
                animated: false, // Static edges for definition
                style: { stroke: '#94a3b8', strokeWidth: 2 },
            }));

            setNodes(flowNodes);
            setEdges(flowEdges);
            return;
        }

        // 2. Handle Execution Trace (Live Mode)
        if (traceData && traceData.steps) {
            const steps = traceData.steps;
            const newNodes = [];
            const newEdges = [];
            const nodeMap = new Map(); // step_id -> node_id

            // Create Nodes
            steps.forEach((step) => {
                const nodeId = step.step_id;
                nodeMap.set(step.step_id, nodeId);

                newNodes.push({
                    id: nodeId,
                    data: { label: step.node_name, stepData: step },
                    position: { x: 0, y: 0 }, // Layout will fix this
                    style: {
                        background: '#ffffff',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        padding: '16px',
                        minWidth: '200px',
                        textAlign: 'left',
                        color: '#1e293b',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                        fontFamily: 'Inter, sans-serif',
                    },
                });
            });

            // Create Edges
            steps.forEach((step, index) => {
                if (step.parent_id && nodeMap.has(step.parent_id)) {
                    newEdges.push({
                        id: `e${step.parent_id}-${step.step_id}`,
                        source: step.parent_id,
                        target: step.step_id,
                        type: 'smoothstep',
                        markerEnd: { type: MarkerType.ArrowClosed },
                        animated: true,
                        style: { stroke: '#94a3b8', strokeWidth: 2 },
                    });
                } else if (index > 0 && !step.parent_id) {
                    // Fallback for linear traces without parent_id
                    const prev = steps[index - 1].step_id;
                    newEdges.push({
                        id: `e${prev}-${step.step_id}`,
                        source: prev,
                        target: step.step_id,
                        type: 'smoothstep',
                        markerEnd: { type: MarkerType.ArrowClosed },
                        animated: true,
                        style: { stroke: '#94a3b8', strokeWidth: 2 },
                    });
                }
            });

            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                newNodes,
                newEdges
            );

            setNodes(layoutedNodes);
            setEdges(layoutedEdges);
            return;
        }
    }, [traceData, workflowData]);

    // Save to history when nodes or edges change (but not during undo/redo)
    const isUndoRedoRef = React.useRef(false);

    useEffect(() => {
        if (workflowData && nodes.length > 0 && !isUndoRedoRef.current) {
            const snapshot = { nodes: JSON.parse(JSON.stringify(nodes)), edges: JSON.parse(JSON.stringify(edges)) };
            setHistory(prev => {
                const newHistory = prev.slice(0, historyIndex + 1);
                return [...newHistory, snapshot];
            });
            setHistoryIndex(prev => prev + 1);
        }
        isUndoRedoRef.current = false;
    }, [nodes, edges]);

    // Keyboard handler for delete (Shift+Delete)
    useEffect(() => {
        const handleKeyDown = (event) => {
            // Only delete if Shift+Delete is pressed
            if ((event.key === 'Delete' || event.key === 'Backspace') && event.shiftKey) {
                const selectedNodes = nodes.filter(node => node.selected);
                const selectedEdges = edges.filter(edge => edge.selected);

                if (selectedNodes.length > 0 || selectedEdges.length > 0) {
                    event.preventDefault();

                    // Remove selected nodes and edges
                    const nodeIdsToRemove = selectedNodes.map(n => n.id);
                    const newNodes = nodes.filter(n => !nodeIdsToRemove.includes(n.id));
                    const newEdges = edges.filter(e =>
                        !selectedEdges.map(se => se.id).includes(e.id) &&
                        !nodeIdsToRemove.includes(e.source) &&
                        !nodeIdsToRemove.includes(e.target)
                    );

                    setNodes(newNodes);
                    setEdges(newEdges);

                    // Notify parent of change
                    if (onWorkflowChange && workflowData) {
                        onWorkflowChange({
                            ...workflowData,
                            nodes: newNodes,
                            edges: newEdges
                        });
                    }
                }
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [nodes, edges, workflowData, onWorkflowChange, setNodes, setEdges]);

    const handleUndo = useCallback(() => {
        if (historyIndex > 0) {
            isUndoRedoRef.current = true;
            const prevState = history[historyIndex - 1];
            setNodes(prevState.nodes);
            setEdges(prevState.edges);
            setHistoryIndex(historyIndex - 1);

            if (onWorkflowChange && workflowData) {
                onWorkflowChange({
                    ...workflowData,
                    nodes: prevState.nodes,
                    edges: prevState.edges
                });
            }
        }
    }, [history, historyIndex, onWorkflowChange, workflowData, setNodes, setEdges]);

    const handleRedo = useCallback(() => {
        if (historyIndex < history.length - 1) {
            isUndoRedoRef.current = true;
            const nextState = history[historyIndex + 1];
            setNodes(nextState.nodes);
            setEdges(nextState.edges);
            setHistoryIndex(historyIndex + 1);

            if (onWorkflowChange && workflowData) {
                onWorkflowChange({
                    ...workflowData,
                    nodes: nextState.nodes,
                    edges: nextState.edges
                });
            }
        }
    }, [history, historyIndex, onWorkflowChange, workflowData, setNodes, setEdges]);

    useEffect(() => {
        if (onWorkflowChange) {
            // Convert ReactFlow types back to workflow types for saving
            const workflowNodes = nodes.map(node => ({
                ...node,
                type: node.type === 'textInput' ? 'textInput' : node.type,
                data: {
                    ...node.data,
                    type: node.type === 'textInput' ? 'input-text' : node.data?.type
                }
            }));
            onWorkflowChange({ nodes: workflowNodes, edges });
        }
    }, [nodes, edges, onWorkflowChange]);

    const handleTextInputChange = useCallback((nodeId, text) => {
        setNodes((nds) =>
            nds.map((node) =>
                node.id === nodeId
                    ? { ...node, data: { ...node.data, text } }
                    : node
            )
        );
    }, [setNodes]);

    const handleTriggerWorkflow = useCallback(async (nodeId, text) => {
        console.log('Triggering workflow from node:', nodeId, 'with text:', text);

        // Get the current workflow
        if (!workflowData) {
            console.error('No workflow loaded');
            return;
        }

        // Prepare the workflow for execution
        const currentNodes = nodesRef.current;
        const currentEdges = edgesRef.current;

        const executionWorkflow = {
            ...workflowData,
            nodes: currentNodes.map(n => ({
                id: n.id,
                type: n.data?.type || n.type, // Use data.type (node definition ID) if available
                position: n.position,
                data: n.data
            })),
            edges: currentEdges.map(e => ({
                id: e.id,
                source: e.source,
                target: e.target
            }))
        };

        console.log('Execution workflow being sent:', JSON.stringify(executionWorkflow, null, 2));

        try {
            const response = await fetch('http://localhost:8080/api/workflows/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(executionWorkflow)
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Workflow execution started:', data.execution_id);

                // Poll for execution status and logs
                const executionId = data.execution_id;
                const pollInterval = setInterval(async () => {
                    try {
                        const statusResponse = await fetch(`http://localhost:8080/api/execution/${executionId}/status`);
                        if (statusResponse.ok) {
                            const status = await statusResponse.json();

                            // Update logs
                            if (status.logs && status.logs.length > 0) {
                                setLogs(status.logs);
                            }

                            // Stop polling if completed or failed
                            if (status.state === 'completed' || status.state === 'failed') {
                                clearInterval(pollInterval);
                                console.log('Workflow execution finished:', status.state);
                            }
                        }
                    } catch (error) {
                        console.error('Error polling execution status:', error);
                    }
                }, 500); // Poll every 500ms

                // Stop polling after 60 seconds max
                setTimeout(() => clearInterval(pollInterval), 60000);
            } else {
                console.error('Failed to execute workflow');
            }
        } catch (error) {
            console.error('Error executing workflow:', error);
        }
    }, [workflowData, setLogs]); // Removed nodes/edges from dependency as we use refs

    const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges, onWorkflowChange]);

    const addNode = () => {
        const id = `new_node_${Date.now()}`;
        const newNode = {
            id,
            position: { x: 100, y: 100 },
            data: {
                label: 'New Node',
                stepData: {
                    node_name: 'New Node',
                    input_data: {},
                    output_data: {},
                    timestamp: new Date().toISOString(),
                    step_id: id
                }
            },
            style: {
                background: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                padding: '16px',
                minWidth: '200px',
                textAlign: 'left',
                color: '#1e293b',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                fontFamily: 'Inter, sans-serif',
            },
        };
        setNodes((nds) => nds.concat(newNode));
    };

    const onDragOver = useCallback((event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback(
        (event) => {
            event.preventDefault();

            const nodeType = event.dataTransfer.getData('application/reactflow');
            const nodeLabel = event.dataTransfer.getData('application/reactflow/label');

            if (!nodeType || !reactFlowInstance) {
                return;
            }

            const position = reactFlowInstance.screenToFlowPosition({
                x: event.clientX,
                y: event.clientY,
            });

            const id = `${nodeType}_${Date.now()}`;
            const newNode = {
                id,
                type: nodeType === 'input-text' ? 'textInput' : 'custom',
                position,
                data: {
                    label: nodeLabel || nodeType,
                    type: nodeType,
                    onTextChange: handleTextInputChange,
                    onTrigger: handleTriggerWorkflow
                },
                style: {
                    background: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '16px',
                    minWidth: '200px',
                    textAlign: 'left',
                    color: '#1e293b',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    fontFamily: 'Inter, sans-serif',
                },
            };

            setNodes((nds) => nds.concat(newNode));
        },
        [reactFlowInstance, setNodes]
    );

    const defaultEdgeOptions = {
        style: { strokeWidth: 2, stroke: '#64748b' },
        type: 'smoothstep',
        animated: false,
    };

    return (
        <div className="h-full w-full relative">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                nodeTypes={nodeTypes}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onNodeClick={(_, node) => onNodeClick(node)}
                onInit={setReactFlowInstance}
                onDrop={onDrop}
                onDragOver={onDragOver}
                defaultEdgeOptions={defaultEdgeOptions}
                fitView
                attributionPosition="bottom-right"
            >
                <Background variant="dots" gap={20} size={0.5} color="#334155" />
                <Controls />
            </ReactFlow>

            <div className="absolute top-4 right-4 flex gap-2 z-10">
                <button
                    onClick={handleUndo}
                    disabled={historyIndex <= 0}
                    className="bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium p-2 rounded-lg shadow-lg transition-colors flex items-center gap-2"
                    title="Undo (Ctrl+Z)"
                >
                    <Undo2 size={18} />
                </button>
                <button
                    onClick={handleRedo}
                    disabled={historyIndex >= history.length - 1}
                    className="bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium p-2 rounded-lg shadow-lg transition-colors flex items-center gap-2"
                    title="Redo (Ctrl+Y)"
                >
                    <Redo2 size={18} />
                </button>
                <button
                    onClick={addNode}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg shadow-lg transition-colors flex items-center gap-2"
                >
                    <span>+ Add Node</span>
                </button>
            </div>
        </div>
    );
};

export default AgentGraph;
