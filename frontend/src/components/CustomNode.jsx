import React from 'react';
import { Handle, Position } from 'reactflow';

const CustomNode = ({ data }) => {
    return (
        <div className="relative">
            {/* Input Handle - Left Side */}
            <Handle
                type="target"
                position={Position.Left}
                id="input"
                style={{
                    background: '#3b82f6',
                    width: '12px',
                    height: '12px',
                    border: '2px solid white',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}
            />

            {/* Node Content */}
            <div className="px-4 py-3">
                <div className="font-semibold text-sm text-slate-800 mb-1">
                    {data.label}
                </div>
                {data.type && (
                    <div className="text-xs text-slate-500">
                        {data.type}
                    </div>
                )}
            </div>

            {/* Output Handle - Right Side */}
            <Handle
                type="source"
                position={Position.Right}
                id="output"
                style={{
                    background: '#10b981',
                    width: '12px',
                    height: '12px',
                    border: '2px solid white',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}
            />
        </div>
    );
};

export default CustomNode;
