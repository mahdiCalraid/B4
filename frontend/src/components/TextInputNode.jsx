import React, { useState } from 'react';
import { Handle, Position } from 'reactflow';
import { Play, PenTool } from 'lucide-react';

const TextInputNode = ({ data, id }) => {
    const [text, setText] = useState(data.text || '');

    const handleTextChange = (e) => {
        setText(e.target.value);
        // Update node data
        if (data.onTextChange) {
            data.onTextChange(id, e.target.value);
        }
    };

    const handleTrigger = () => {
        if (data.onTrigger) {
            data.onTrigger(id, text);
        }
    };

    return (
        <div className="relative bg-white border-2 border-emerald-400 rounded-lg shadow-lg min-w-[350px]">
            {/* Output Handle - Right Side */}
            <Handle
                type="source"
                position={Position.Right}
                id="output"
                style={{
                    background: '#10b981',
                    width: '16px',
                    height: '16px',
                    border: '3px solid white',
                    boxShadow: '0 2px 6px rgba(16, 185, 129, 0.4)'
                }}
            />

            {/* Node Content */}
            <div className="p-4">
                {/* Header */}
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center flex-shrink-0">
                        <PenTool size={22} className="text-white" />
                    </div>
                    <div className="flex-1">
                        <div className="font-semibold text-base text-emerald-900">
                            {data.label || 'Text Input'}
                        </div>
                        <div className="text-xs text-emerald-600">
                            Enter text to trigger workflow
                        </div>
                    </div>
                </div>

                {/* Always Visible Input Area */}
                <div className="space-y-3">
                    <textarea
                        value={text}
                        onChange={handleTextChange}
                        placeholder={data.placeholder || "Enter your text here..."}
                        className="w-full px-3 py-2 text-sm border-2 border-emerald-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 resize-none bg-white"
                        rows={6}
                    />

                    {/* Trigger Button */}
                    <button
                        onClick={handleTrigger}
                        disabled={!text.trim()}
                        className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium py-2.5 px-4 rounded-md text-sm transition-colors shadow-md"
                    >
                        <Play size={16} fill="currentColor" />
                        <span>Run Workflow</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TextInputNode;
