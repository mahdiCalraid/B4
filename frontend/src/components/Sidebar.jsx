import React, { useState, useEffect } from 'react';
import { RefreshCw, FileText, Plus, ChevronDown, ChevronRight, Users, Wrench, Eye, EyeOff } from 'lucide-react';

const SidebarSection = ({ title, icon: Icon, items = [], renderItem, defaultOpen = false, onRefresh, loading, extraAction, children }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    const [hiddenIds, setHiddenIds] = useState(new Set());
    const [showHidden, setShowHidden] = useState(false);

    const toggleHide = (id) => {
        const newHidden = new Set(hiddenIds);
        if (newHidden.has(id)) {
            newHidden.delete(id);
        } else {
            newHidden.add(id);
        }
        setHiddenIds(newHidden);
    };

    const visibleItems = items.filter(item => !hiddenIds.has(item.id));
    const hiddenItems = items.filter(item => hiddenIds.has(item.id));

    return (
        <div className="border-b border-slate-700 last:border-0 flex flex-col min-h-0">
            <div
                className="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-800/50 transition-colors shrink-0"
                onClick={() => setIsOpen(!isOpen)}
            >
                <div className="flex items-center gap-2 text-slate-100 font-semibold">
                    {Icon && <Icon size={18} className="text-slate-400" />}
                    <span>{title}</span>
                    {items.length > 0 && <span className="text-xs text-slate-500 font-normal ml-1">({visibleItems.length})</span>}
                </div>
                <div className="flex items-center gap-2">
                    {onRefresh && (
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onRefresh();
                            }}
                            className="p-1 text-slate-400 hover:text-slate-100 hover:bg-slate-700 rounded transition-colors"
                            title="Refresh"
                        >
                            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
                        </button>
                    )}
                    {isOpen ? <ChevronDown size={16} className="text-slate-500" /> : <ChevronRight size={16} className="text-slate-500" />}
                </div>
            </div>

            {isOpen && (
                <div className="flex flex-col min-h-0">
                    {/* Visible Items - Scrollable */}
                    {items.length > 0 && renderItem ? (
                        <div className="px-2 space-y-1 overflow-y-auto max-h-60 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                            {visibleItems.length === 0 ? (
                                <div className="text-slate-500 text-sm text-center py-4 italic">
                                    No visible items
                                </div>
                            ) : (
                                visibleItems.map(item => (
                                    <div key={item.id} className="group relative pr-8">
                                        {renderItem(item)}
                                        <button
                                            onClick={() => toggleHide(item.id)}
                                            className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-500 hover:text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity"
                                            title="Hide"
                                        >
                                            <EyeOff size={14} />
                                        </button>
                                    </div>
                                ))
                            )}
                            {extraAction && (
                                <div className="pt-2 px-1 pb-2">
                                    {extraAction}
                                </div>
                            )}
                        </div>
                    ) : (
                        // Fallback for sections without items/renderItem, using children directly
                        <div className="pb-2">
                            {children}
                        </div>
                    )}


                    {/* Hidden Items Section */}
                    {hiddenItems.length > 0 && (
                        <div className="px-4 py-2 border-t border-slate-800 bg-slate-900/50 shrink-0">
                            <button
                                onClick={() => setShowHidden(!showHidden)}
                                className="flex items-center gap-2 text-xs text-slate-500 hover:text-slate-300 w-full"
                            >
                                {showHidden ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                                <span>Hidden Items ({hiddenItems.length})</span>
                            </button>

                            {showHidden && (
                                <div className="mt-2 space-y-1 max-h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                                    {hiddenItems.map(item => (
                                        <div key={item.id} className="flex items-center justify-between px-2 py-1.5 rounded bg-slate-800/50 text-slate-400 text-xs group">
                                            <span className="truncate max-w-[140px]">{item.name}</span>
                                            <button
                                                onClick={() => toggleHide(item.id)}
                                                className="text-slate-500 hover:text-blue-400"
                                                title="Restore"
                                            >
                                                <Eye size={12} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

const Sidebar = ({ onSelectWorkflow }) => {
    const [workflows, setWorkflows] = useState([]);
    const [nodes, setNodes] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [wfResponse, nodesResponse] = await Promise.all([
                fetch('http://localhost:8080/api/workflows'),
                fetch('http://localhost:8080/api/nodes')
            ]);

            const wfData = await wfResponse.json();
            const nodesData = await nodesResponse.json();

            setWorkflows(wfData.workflows || []);
            setNodes(nodesData.nodes || []);
        } catch (error) {
            console.error('Failed to fetch data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleCreateWorkflow = async () => {
        setLoading(true);
        try {
            const newWorkflow = {
                name: "Untitled Workflow",
                description: "New empty workflow",
                nodes: [],
                edges: []
            };

            const response = await fetch('http://localhost:8080/api/workflows', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newWorkflow),
            });

            if (response.ok) {
                await fetchData();
            }
        } catch (error) {
            console.error('Failed to create workflow:', error);
        } finally {
            setLoading(false);
        }
    };

    const onDragStart = (event, nodeType, nodeLabel) => {
        event.dataTransfer.setData('application/reactflow', nodeType);
        event.dataTransfer.setData('application/reactflow/label', nodeLabel);
        event.dataTransfer.effectAllowed = 'move';
    };

    return (
        <div className="w-64 bg-slate-900 border-r border-slate-700 flex flex-col h-full overflow-y-auto">
            {/* Workflows Section */}
            <SidebarSection
                title="Workflows"
                icon={FileText}
                items={workflows}
                defaultOpen={true}
                onRefresh={fetchData}
                loading={loading}
                extraAction={
                    <button
                        onClick={handleCreateWorkflow}
                        disabled={loading}
                        className="w-full flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 px-4 rounded-md text-xs font-medium transition-colors border border-slate-700 disabled:opacity-50"
                    >
                        <Plus size={14} />
                        New Workflow
                    </button>
                }
                renderItem={(wf) => (
                    <button
                        onClick={() => onSelectWorkflow(wf.id)}
                        className="w-full text-left px-3 py-2 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors flex items-center gap-2 group"
                    >
                        <div className="w-1.5 h-1.5 rounded-full bg-slate-600 group-hover:bg-blue-400 transition-colors shrink-0" />
                        <span className="truncate text-sm">{wf.name || 'Untitled Workflow'}</span>
                    </button>
                )}
            />

            {/* Node Library Section */}
            <SidebarSection
                title="Node Library"
                icon={Wrench}
                items={nodes}
                defaultOpen={true}
                renderItem={(node) => (
                    <div
                        className="w-full text-left px-3 py-2 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors flex items-center gap-2 cursor-grab active:cursor-grabbing border border-transparent hover:border-slate-700"
                        draggable
                        onDragStart={(event) => onDragStart(event, node.id, node.name)}
                    >
                        <div className="w-6 h-6 rounded bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-400 border border-slate-700 shrink-0">
                            {node.name.substring(0, 2).toUpperCase()}
                        </div>
                        <div className="flex flex-col min-w-0">
                            <span className="truncate text-sm font-medium">{node.name}</span>
                            <span className="truncate text-xs text-slate-500">{node.category}</span>
                        </div>
                    </div>
                )}
            />

            {/* Agents Section (Placeholder) */}
            <SidebarSection title="Agents" icon={Users} items={[]}>
                <div className="px-4 py-2 text-xs text-slate-500 italic">
                    Agent definitions will appear here.
                </div>
            </SidebarSection>
        </div>
    );
};

export default Sidebar;
