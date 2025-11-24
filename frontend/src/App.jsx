import React, { useState, useEffect, useCallback } from 'react';
import AgentGraph from './components/AgentGraph';
import ExecutionLog from './components/ExecutionLog';
import Sidebar from './components/Sidebar';
import { Activity, Layers, Play, Save } from 'lucide-react';

function App() {
  const [traceData, setTraceData] = useState(null);
  const [workflowData, setWorkflowData] = useState(null);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(null);
  const [isDirty, setIsDirty] = useState(false);
  const [currentGraphState, setCurrentGraphState] = useState({ nodes: [], edges: [] });
  const [showUnsavedModal, setShowUnsavedModal] = useState(false);
  const [pendingWorkflowId, setPendingWorkflowId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [rightPanelWidth, setRightPanelWidth] = useState(384); // Default 384px (w-96)
  const [isResizing, setIsResizing] = useState(false);

  useEffect(() => {
    // Poll for trace data (mock or real)
    const interval = setInterval(async () => {
      try {
        // In a real app, we might poll execution status here
      } catch (e) {
        console.error(e);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const addLog = (message, details = null) => {
    setLogs(prev => [...prev, { message, details, timestamp: new Date().toISOString() }]);
  };

  const saveWorkflow = async () => {
    if (!workflowData) return;

    const updatedWorkflow = {
      ...workflowData,
      nodes: currentGraphState.nodes,
      edges: currentGraphState.edges,
      updated_at: new Date().toISOString()
    };

    try {
      const response = await fetch('http://localhost:8080/api/workflows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedWorkflow)
      });

      if (response.ok) {
        console.log("Workflow saved successfully");
        setIsDirty(false);
        setWorkflowData(updatedWorkflow); // Update local state
        return true;
      }
    } catch (error) {
      console.error("Failed to save workflow:", error);
      return false;
    }
    return false;
  };

  // Helper to check if graph has truly changed
  const hasGraphChanged = (original, current) => {
    if (!original) return false;
    if (original.nodes.length !== current.nodes.length) return true;
    if (original.edges.length !== current.edges.length) return true;

    // Check nodes (simplified: id, position, data.label)
    // We skip internal ReactFlow fields like 'width', 'height', 'selected', 'dragging'
    const originalNodeMap = new Map(original.nodes.map(n => [n.id, n]));
    for (const currNode of current.nodes) {
      const origNode = originalNodeMap.get(currNode.id);
      if (!origNode) return true;
      if (Math.round(currNode.position.x) !== Math.round(origNode.position.x)) return true;
      if (Math.round(currNode.position.y) !== Math.round(origNode.position.y)) return true;
      // Deep check data if needed, for now check label
      if (currNode.data?.label !== origNode.data?.label) return true;
    }

    // Check edges
    const originalEdgeMap = new Map(original.edges.map(e => [e.id, e]));
    for (const currEdge of current.edges) {
      const origEdge = originalEdgeMap.get(currEdge.id);
      if (!origEdge) return true;
      if (currEdge.source !== origEdge.source) return true;
      if (currEdge.target !== origEdge.target) return true;
    }

    return false;
  };

  const handleWorkflowChange = useCallback((state) => {
    if (workflowData) {
      setCurrentGraphState(state);
      const changed = hasGraphChanged(workflowData, state);
      setIsDirty(changed);
    }
  }, [workflowData]);

  const handleSelectWorkflow = async (id) => {
    if (selectedWorkflowId === id) return;

    if (isDirty) {
      setPendingWorkflowId(id);
      setShowUnsavedModal(true);
      return;
    }

    loadWorkflow(id);
  };

  const loadWorkflow = async (id) => {
    console.log("Loading workflow:", id);
    setSelectedWorkflowId(id);
    try {
      const response = await fetch(`http://localhost:8080/api/workflows/${id}`);
      if (response.ok) {
        const workflow = await response.json();
        setTraceData(null);
        setWorkflowData(workflow);
        setIsDirty(false);
        setCurrentGraphState({ nodes: workflow.nodes || [], edges: workflow.edges || [] });
        setLogs([]); // Clear logs on new workflow
      }
    } catch (error) {
      console.error("Failed to fetch workflow:", error);
    }
  };

  const handleModalAction = async (action) => {
    setShowUnsavedModal(false);
    if (action === 'save') {
      const saved = await saveWorkflow();
      if (saved && pendingWorkflowId) {
        loadWorkflow(pendingWorkflowId);
      }
    } else if (action === 'discard') {
      if (pendingWorkflowId) {
        loadWorkflow(pendingWorkflowId);
      }
    } else {
      // Cancel: do nothing, stay on current
      setPendingWorkflowId(null);
    }
  };

  const handleNodeClick = (node) => {
    console.log("Node clicked:", node);
    // Check if it's a trigger node
    // We need to know the type. In workflowData.nodes, we have the type.
    // But 'node' here comes from ReactFlow, which might have 'type' property if we set it,
    // or we look it up in workflowData.

    // For now, let's assume we can check the label or some data property
    // Ideally, we should have 'type' in the node data.
    // Let's check if the label says "Manual Trigger" or if we can match it to the registry.
    // Since we haven't fully implemented the palette to set types, let's just check the label for this test.

    if (node.data?.label === "Manual Trigger" || node.data?.type === "trigger-manual") {
      addLog("started");
    }
  };

  // Resize handlers for right panel
  const handleMouseDown = (e) => {
    setIsResizing(true);
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;

      const newWidth = window.innerWidth - e.clientX;
      // Constrain between 256px and 800px
      if (newWidth >= 256 && newWidth <= 800) {
        setRightPanelWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 font-sans overflow-hidden">
      {/* Left Sidebar */}
      <Sidebar onSelectWorkflow={handleSelectWorkflow} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-14 bg-slate-900 border-b border-slate-700 flex items-center justify-between px-4 shrink-0">
          <div className="flex items-center gap-2">
            <Layers className="text-blue-500" size={20} />
            <h1 className="font-bold text-lg tracking-tight text-slate-100">
              Map of Agents <span className="text-slate-500 font-normal text-sm ml-2">v0.2.0</span>
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-full border border-slate-700">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-xs font-medium text-slate-300">System Online</span>
            </div>
            {workflowData && (
              <button
                onClick={saveWorkflow}
                className={`px-4 py-1.5 rounded-md text-sm font-medium flex items-center gap-2 transition-colors shadow-lg ${isDirty ? 'bg-amber-600 hover:bg-amber-500 text-white' : 'bg-slate-700 text-slate-400'}`}
              >
                <Save size={14} fill="currentColor" />
                {isDirty ? 'Save Changes' : 'Saved'}
              </button>
            )}
            <button disabled className="bg-slate-800 text-slate-500 cursor-not-allowed px-4 py-1.5 rounded-md text-sm font-medium flex items-center gap-2 transition-colors border border-slate-700">
              <Play size={14} fill="currentColor" />
              Run Workflow
            </button>
          </div>
        </header>

        {/* Graph Area */}
        <div className="flex-1 flex relative bg-slate-950 overflow-hidden">
          <div className="flex-1 relative">
            <AgentGraph
              traceData={traceData}
              workflowData={workflowData}
              onWorkflowChange={handleWorkflowChange}
              onNodeClick={handleNodeClick}
              setLogs={setLogs}
            />

            {/* Unsaved Changes Modal */}
            {showUnsavedModal && (
              <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="bg-slate-900 border border-slate-700 rounded-lg shadow-2xl p-6 max-w-md w-full">
                  <h3 className="text-lg font-semibold text-slate-100 mb-2">Unsaved Changes</h3>
                  <p className="text-slate-400 mb-6">You have unsaved changes in the current workflow. What would you like to do?</p>
                  <div className="flex justify-end gap-3">
                    <button
                      onClick={() => handleModalAction('cancel')}
                      className="px-4 py-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-md transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleModalAction('discard')}
                      className="px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-md transition-colors"
                    >
                      Discard
                    </button>
                    <button
                      onClick={() => handleModalAction('save')}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md transition-colors shadow-lg"
                    >
                      Save & Switch
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel: Execution Log with Resize Handle */}
          <div
            className="relative flex"
            style={{ width: `${rightPanelWidth}px` }}
          >
            {/* Resize Handle */}
            <div
              onMouseDown={handleMouseDown}
              className={`w-1 bg-slate-700 hover:bg-blue-500 cursor-col-resize transition-colors shrink-0 ${isResizing ? 'bg-blue-500' : ''}`}
              style={{ touchAction: 'none' }}
            />
            <ExecutionLog logs={logs} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
